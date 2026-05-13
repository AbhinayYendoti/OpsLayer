"use client";

import { AlertCircle, CheckCircle2, CircleDashed, ShieldAlert } from "lucide-react";
import { useEffect, useRef } from "react";

import type { WorkflowStep } from "@/lib/types";

const agentClass: Record<string, string> = {
  Researcher: "text-agent-researcher border-agent-researcher/40 bg-agent-researcher/10",
  Analyst: "text-agent-analyst border-agent-analyst/40 bg-agent-analyst/10",
  Executor: "text-agent-executor border-agent-executor/40 bg-agent-executor/10",
  Manager: "text-agent-manager border-agent-manager/40 bg-agent-manager/10",
  Safety: "text-agent-safety border-agent-safety/40 bg-agent-safety/10",
};

function statusIcon(status: WorkflowStep["status"]) {
  if (status === "done" || status === "complete") {
    return <CheckCircle2 className="h-4 w-4 text-agent-manager" />;
  }
  if (status === "waiting_approval") {
    return <ShieldAlert className="h-4 w-4 text-agent-safety" />;
  }
  if (status === "error") {
    return <AlertCircle className="h-4 w-4 text-agent-safety" />;
  }
  return <CircleDashed className="h-4 w-4 animate-spin text-accent" />;
}

interface WorkflowLogProps {
  steps: WorkflowStep[];
  errorMessage?: string;
}

export function WorkflowLog({ steps, errorMessage }: WorkflowLogProps) {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [steps.length]);

  return (
    <section className="px-8 py-6">
      <div className="mx-auto max-w-5xl">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-text-primary">Live Workflow Log</h2>
          <span className="text-xs text-text-secondary">{steps.length} events</span>
        </div>

        {errorMessage ? (
          <div className="mb-4 rounded-md border border-agent-safety/40 bg-agent-safety/10 px-4 py-3 text-sm text-text-primary">
            {errorMessage}
          </div>
        ) : null}

        <div className="space-y-3">
          {steps.length === 0 ? (
            <div className="rounded-lg border border-dashed border-border bg-surface px-4 py-10 text-center text-sm text-text-secondary">
              Workflow steps will stream here as soon as a run starts.
            </div>
          ) : (
            steps.map((step) => (
              <article key={`${step.workflow_id}-${step.step}`} className="rounded-lg border border-border bg-surface p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex min-w-0 gap-3">
                    <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-border bg-background text-xs text-text-secondary">
                      {step.step}
                    </div>
                    <div className="min-w-0">
                      <div className="mb-1 flex flex-wrap items-center gap-2">
                        <span
                          className={`rounded-md border px-2 py-0.5 text-xs font-medium ${
                            agentClass[step.agent] ?? "border-border bg-background text-text-secondary"
                          }`}
                        >
                          {step.agent}
                        </span>
                        <span className="flex items-center gap-1 text-xs capitalize text-text-secondary">
                          {statusIcon(step.status)}
                          {step.status.replace("_", " ")}
                        </span>
                      </div>
                      <p className="text-sm leading-6 text-text-primary">{step.action}</p>
                    </div>
                  </div>
                  <time className="shrink-0 text-xs text-text-secondary">
                    {new Date(step.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </time>
                </div>

                {step.result ? (
                  <pre className="mt-3 max-h-56 overflow-auto rounded-md border border-border bg-background p-3 text-xs leading-5 text-text-secondary">
                    {step.result}
                  </pre>
                ) : null}
              </article>
            ))
          )}
          <div ref={endRef} />
        </div>
      </div>
    </section>
  );
}
