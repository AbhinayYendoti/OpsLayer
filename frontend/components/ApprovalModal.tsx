"use client";

import { Check, X } from "lucide-react";

import { useApproval } from "@/hooks/useApproval";
import type { ApprovalRequest } from "@/lib/types";

interface ApprovalModalProps {
  pendingApproval: ApprovalRequest | null;
  onResolved: () => void;
  onError: (message: string) => void;
}

export function ApprovalModal({ pendingApproval, onResolved, onError }: ApprovalModalProps) {
  const { approve, reject, isSubmitting } = useApproval(pendingApproval, onResolved, onError);

  if (!pendingApproval) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/75 px-4 backdrop-blur-sm">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="approval-title"
        className="w-full max-w-2xl rounded-lg border border-border bg-surface p-5 shadow-2xl"
      >
        <div className="mb-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-agent-safety">Approval required</p>
          <h2 id="approval-title" className="mt-1 text-lg font-semibold text-text-primary">
            The Executor wants to perform a write action
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            This workflow is paused. It cannot continue until you approve or reject this action.
          </p>
        </div>

        <div className="space-y-3 rounded-md border border-border bg-background p-4">
          <div>
            <div className="text-xs uppercase tracking-wide text-text-secondary">Tool</div>
            <div className="mt-1 font-mono text-sm text-text-primary">{pendingApproval.tool}</div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wide text-text-secondary">Action</div>
            <div className="mt-1 text-sm leading-6 text-text-primary">{pendingApproval.action}</div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wide text-text-secondary">Parameters</div>
            <pre className="mt-2 max-h-64 overflow-auto rounded-md border border-border bg-surface p-3 text-xs leading-5 text-text-secondary">
              {JSON.stringify(pendingApproval.parameters, null, 2)}
            </pre>
          </div>
        </div>

        <div className="mt-5 flex justify-end gap-3">
          <button
            onClick={reject}
            disabled={isSubmitting}
            className="flex h-10 items-center gap-2 rounded-md border border-border px-4 text-sm font-medium text-text-primary transition hover:bg-surface-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            <X className="h-4 w-4" />
            Reject
          </button>
          <button
            onClick={approve}
            disabled={isSubmitting}
            className="flex h-10 items-center gap-2 rounded-md bg-agent-manager px-4 text-sm font-medium text-white transition hover:bg-green-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Check className="h-4 w-4" />
            Approve
          </button>
        </div>
      </div>
    </div>
  );
}
