"use client";

import { Play, RotateCcw } from "lucide-react";

const DEMOS = [
  {
    icon: "📧",
    label: "CRM Update",
    prompt: "Find emails from Acme Corp this week and add a CRM note summarizing their status.",
  },
  {
    icon: "💬",
    label: "Slack Digest",
    prompt: "Summarize today's messages in the #sales channel and give me the key highlights.",
  },
  {
    icon: "🎯",
    label: "Lead Research",
    prompt: "Research TechCorp across Gmail and Slack, draft a CRM note and a follow-up email.",
  },
];

interface WorkflowInputProps {
  value: string;
  status: "idle" | "running" | "complete" | "error";
  onChange: (value: string) => void;
  onRun: (value: string) => void;
  onReset: () => void;
}

export function WorkflowInput({ value, status, onChange, onRun, onReset }: WorkflowInputProps) {
  const isRunning = status === "running";
  const canRun = value.trim().length >= 3 && !isRunning;

  return (
    <section className="border-b border-border bg-background px-8 py-6">
      <div className="mx-auto max-w-5xl">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-xl font-semibold text-text-primary">Workspace</h1>
            <p className="mt-1 text-sm text-text-secondary">
              Run visible, approval-gated workflows across Gmail, Slack, and CRM.
            </p>
          </div>
          <button
            onClick={onReset}
            className="flex h-9 items-center gap-2 rounded-md border border-border px-3 text-sm text-text-secondary transition hover:bg-surface-hover hover:text-text-primary"
          >
            <RotateCcw className="h-4 w-4" />
            Reset
          </button>
        </div>

        <div className="rounded-lg border border-border bg-surface p-4">
          <textarea
            value={value}
            maxLength={500}
            onChange={(event) => onChange(event.target.value)}
            placeholder="What workflow should I run?"
            className="min-h-[112px] w-full resize-none bg-transparent text-sm leading-6 text-text-primary outline-none placeholder:text-text-secondary"
          />
          <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap gap-2">
              {DEMOS.map((demo) => (
                <button
                  key={demo.label}
                  onClick={() => onChange(demo.prompt)}
                  disabled={isRunning}
                  className="flex h-8 items-center gap-2 rounded-md border border-border px-2.5 text-xs text-text-secondary transition hover:bg-surface-hover hover:text-text-primary disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <span aria-hidden>{demo.icon}</span>
                  {demo.label}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-text-secondary">{value.length}/500</span>
              <button
                onClick={() => onRun(value)}
                disabled={!canRun}
                className="flex h-9 items-center gap-2 rounded-md bg-accent px-4 text-sm font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Play className="h-4 w-4" />
                {isRunning ? "Running" : "Run Workflow"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
