"use client";

import { useCallback, useState } from "react";

import { api } from "@/lib/api";
import type { ApprovalRequest } from "@/lib/types";

export function useApproval(
  pendingApproval: ApprovalRequest | null,
  onResolved: () => void,
  onError: (message: string) => void,
) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const submitDecision = useCallback(
    async (decision: "approved" | "rejected") => {
      if (!pendingApproval || isSubmitting) {
        return;
      }

      setIsSubmitting(true);
      try {
        await api.submitApproval(pendingApproval.workflowId, decision);
        onResolved();
      } catch (error) {
        onError(error instanceof Error ? error.message : "Unable to submit approval decision.");
      } finally {
        setIsSubmitting(false);
      }
    },
    [isSubmitting, onError, onResolved, pendingApproval],
  );

  return {
    isSubmitting,
    approve: () => submitDecision("approved"),
    reject: () => submitDecision("rejected"),
  };
}
