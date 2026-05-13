"use client";

import { Clock3, FileText, Plus, Settings } from "lucide-react";

import type { WorkflowHistoryItem } from "@/lib/types";

interface SidebarProps {
  history: WorkflowHistoryItem[];
  onNewWorkflow: () => void;
}

export function Sidebar({ history, onNewWorkflow }: SidebarProps) {
  return (
    <aside className="flex h-screen w-[260px] shrink-0 flex-col border-r border-border bg-surface px-3 py-4">
      <div className="mb-5 flex items-center gap-3 px-2">
        <div className="grid h-8 w-8 place-items-center rounded-md border border-border bg-background text-sm font-semibold text-accent">
          L
        </div>
        <div>
          <p className="text-sm font-semibold text-text-primary">Libra AI</p>
          <p className="text-xs text-text-secondary">Coworker</p>
        </div>
      </div>

      <button
        onClick={onNewWorkflow}
        className="mb-5 flex h-9 items-center gap-2 rounded-md bg-accent px-3 text-sm font-medium text-white transition hover:bg-blue-500"
      >
        <Plus className="h-4 w-4" />
        New Workflow
      </button>

      <div className="mb-2 px-2 text-xs font-medium uppercase tracking-wide text-text-secondary">Recent</div>
      <div className="flex-1 space-y-1 overflow-y-auto">
        {history.length === 0 ? (
          <div className="px-2 py-2 text-xs leading-5 text-text-secondary">
            Completed and running workflows will appear here.
          </div>
        ) : (
          history.map((item) => (
            <div
              key={item.id}
              className="rounded-md px-2 py-2 text-sm text-text-secondary transition hover:bg-surface-hover hover:text-text-primary"
            >
              <div className="flex items-center gap-2">
                <Clock3 className="h-3.5 w-3.5 shrink-0" />
                <span className="truncate">{item.input}</span>
              </div>
              <div className="mt-1 pl-5 text-[11px] capitalize text-text-secondary">{item.status}</div>
            </div>
          ))
        )}
      </div>

      <div className="space-y-1 border-t border-border pt-3">
        <button className="flex w-full items-center gap-2 rounded-md px-2 py-2 text-sm text-text-secondary transition hover:bg-surface-hover hover:text-text-primary">
          <Settings className="h-4 w-4" />
          Settings
        </button>
        <a
          href="https://docs.crewai.com/"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-2 rounded-md px-2 py-2 text-sm text-text-secondary transition hover:bg-surface-hover hover:text-text-primary"
        >
          <FileText className="h-4 w-4" />
          Docs
        </a>
      </div>
    </aside>
  );
}
