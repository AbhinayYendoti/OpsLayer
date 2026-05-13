"use client";

import { useCallback, useRef, useState } from "react";

import { API_URL, api } from "@/lib/api";
import type { ApprovalRequest, WorkflowHistoryItem, WorkflowStatus, WorkflowStep } from "@/lib/types";

export function useWorkflow() {
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [steps, setSteps] = useState<WorkflowStep[]>([]);
  const [status, setStatus] = useState<WorkflowStatus>("idle");
  const [pendingApproval, setPendingApproval] = useState<ApprovalRequest | null>(null);
  const [finalResult, setFinalResult] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [history, setHistory] = useState<WorkflowHistoryItem[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  const closeStream = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }, []);

  const resetWorkflow = useCallback(() => {
    closeStream();
    setWorkflowId(null);
    setInput("");
    setSteps([]);
    setStatus("idle");
    setPendingApproval(null);
    setFinalResult("");
    setErrorMessage("");
  }, [closeStream]);

  const startWorkflow = useCallback(
    async (nextInput: string) => {
      const trimmed = nextInput.trim();
      if (!trimmed || status === "running") {
        return;
      }

      closeStream();
      setSteps([]);
      setPendingApproval(null);
      setFinalResult("");
      setErrorMessage("");
      setStatus("running");

      try {
        const { workflow_id } = await api.startWorkflow(trimmed);
        setWorkflowId(workflow_id);
        setHistory((prev) => [
          { id: workflow_id, input: trimmed, status: "running", createdAt: new Date().toISOString() },
          ...prev.slice(0, 7),
        ]);

        const es = new EventSource(`${API_URL}/api/workflow/${workflow_id}/stream`);
        eventSourceRef.current = es;

        es.onmessage = async (event) => {
          const step = JSON.parse(event.data) as WorkflowStep;
          setSteps((prev) => [...prev, step]);

          if (step.status === "waiting_approval") {
            setPendingApproval({
              ...step,
              workflowId: workflow_id,
              tool: step.tool ?? "unknown_tool",
              parameters: step.parameters ?? {},
            });
            return;
          }

          if (step.status === "complete" || step.status === "error") {
            const nextStatus = step.status === "complete" ? "complete" : "error";
            setStatus(nextStatus);
            setFinalResult(step.result ?? "");
            setHistory((prev) =>
              prev.map((item) => (item.id === workflow_id ? { ...item, status: nextStatus } : item)),
            );
            closeStream();
          }
        };

        es.onerror = () => {
          setStatus("error");
          setErrorMessage("The live workflow stream disconnected. The backend may still be running the workflow.");
          setHistory((prev) => prev.map((item) => (item.id === workflow_id ? { ...item, status: "error" } : item)));
          closeStream();
        };
      } catch (error) {
        setStatus("error");
        setErrorMessage(error instanceof Error ? error.message : "Unable to start workflow.");
      }
    },
    [closeStream, status],
  );

  return {
    workflowId,
    input,
    setInput,
    steps,
    status,
    pendingApproval,
    setPendingApproval,
    finalResult,
    errorMessage,
    setErrorMessage,
    history,
    startWorkflow,
    resetWorkflow,
  };
}
