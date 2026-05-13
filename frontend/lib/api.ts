import type { WorkflowResult } from "./types";

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = "Request failed. Please try again.";
    try {
      const data = (await response.json()) as { detail?: string };
      if (data.detail) {
        message = data.detail;
      }
    } catch {
      // Keep safe user-facing fallback.
    }
    throw new Error(message);
  }
  return (await response.json()) as T;
}

export const api = {
  async startWorkflow(input: string): Promise<{ workflow_id: string }> {
    const response = await fetch(`${API_URL}/api/workflow/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input }),
    });
    return parseJson<{ workflow_id: string }>(response);
  },

  async submitApproval(workflowId: string, decision: "approved" | "rejected"): Promise<{ success: boolean }> {
    const response = await fetch(`${API_URL}/api/workflow/${workflowId}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision }),
    });
    return parseJson<{ success: boolean }>(response);
  },

  async getResult(workflowId: string): Promise<WorkflowResult> {
    const response = await fetch(`${API_URL}/api/workflow/${workflowId}/result`, {
      cache: "no-store",
    });
    return parseJson<WorkflowResult>(response);
  },
};
