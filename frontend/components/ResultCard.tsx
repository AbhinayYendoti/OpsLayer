"use client";

import { Copy, RotateCw } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface ResultCardProps {
  result: string;
  onRunAgain: () => void;
}

export function ResultCard({ result, onRunAgain }: ResultCardProps) {
  if (!result) {
    return null;
  }

  return (
    <section className="border-t border-border bg-background px-8 py-6 pb-12">
      <div className="mx-auto max-w-5xl rounded-lg border border-border bg-surface p-5">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-sm font-semibold text-text-primary">Final Result</h2>
          <div className="flex gap-2">
            <button
              onClick={() => navigator.clipboard.writeText(result)}
              className="flex h-8 items-center gap-2 rounded-md border border-border px-2.5 text-xs text-text-secondary transition hover:bg-surface-hover hover:text-text-primary"
            >
              <Copy className="h-3.5 w-3.5" />
              Copy
            </button>
            <button
              onClick={onRunAgain}
              className="flex h-8 items-center gap-2 rounded-md border border-border px-2.5 text-xs text-text-secondary transition hover:bg-surface-hover hover:text-text-primary"
            >
              <RotateCw className="h-3.5 w-3.5" />
              Run Again
            </button>
          </div>
        </div>
        <div className="prose prose-invert max-w-none prose-p:text-text-secondary prose-li:text-text-secondary prose-headings:text-text-primary">
          <ReactMarkdown>{result}</ReactMarkdown>
        </div>
      </div>
    </section>
  );
}
