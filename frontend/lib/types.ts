export type WorkflowStatus = "idle" | "running" | "complete" | "error";

export type WorkflowStepStatus =
  | "running"
  | "done"
  | "waiting_approval"
  | "complete"
  | "error";

export type AgentName = "Manager" | "Researcher" | "Analyst" | "Executor" | "Safety";

export interface WorkflowStep {
  workflow_id: string;
  step: number;
  agent: AgentName | string;
  action: string;
  status: WorkflowStepStatus;
  result?: string;
  timestamp: string;
  tool?: string;
  parameters?: Record<string, unknown>;
}

export interface ApprovalRequest extends WorkflowStep {
  workflowId: string;
  tool: string;
  parameters: Record<string, unknown>;
}

export interface WorkflowResult {
  final_result: string;
  steps: WorkflowStep[];
  status: "running" | "complete" | "error";
}

export interface WorkflowHistoryItem {
  id: string;
  input: string;
  status: WorkflowStatus;
  createdAt: string;
}
