"use client";

import { ApprovalModal } from "@/components/ApprovalModal";
import { ResultCard } from "@/components/ResultCard";
import { Sidebar } from "@/components/Sidebar";
import { WorkflowInput } from "@/components/WorkflowInput";
import { WorkflowLog } from "@/components/WorkflowLog";
import { useWorkflow } from "@/hooks/useWorkflow";

export default function WorkspacePage() {
  const workflow = useWorkflow();

  return (
    <main className="flex h-screen overflow-hidden bg-background text-text-primary">
      <Sidebar history={workflow.history} onNewWorkflow={workflow.resetWorkflow} />
      <div className="min-w-0 flex-1 overflow-y-auto">
        <WorkflowInput
          value={workflow.input}
          status={workflow.status}
          onChange={workflow.setInput}
          onRun={workflow.startWorkflow}
          onReset={workflow.resetWorkflow}
        />
        <WorkflowLog steps={workflow.steps} errorMessage={workflow.errorMessage} />
        <ResultCard result={workflow.finalResult} onRunAgain={() => workflow.startWorkflow(workflow.input)} />
      </div>
      <ApprovalModal
        pendingApproval={workflow.pendingApproval}
        onResolved={() => workflow.setPendingApproval(null)}
        onError={(message) => {
          workflow.setPendingApproval(null);
          workflow.setErrorMessage(message);
        }}
      />
    </main>
  );
}
