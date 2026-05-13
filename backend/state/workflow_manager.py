"""In-memory workflow sessions and SSE event queues."""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


TERMINAL_STATUSES = {"complete", "error"}


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


@dataclass
class WorkflowSession:
    """Runtime state for one workflow execution."""

    workflow_id: str
    user_input: str
    queue: asyncio.Queue[dict[str, Any] | None] = field(default_factory=asyncio.Queue)
    approval_event: asyncio.Event = field(default_factory=asyncio.Event)
    approval_result: str = "pending"
    status: str = "running"
    steps: list[dict[str, Any]] = field(default_factory=list)
    final_result: str = ""
    pending_approval: dict[str, Any] | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    task: asyncio.Task[Any] | None = None
    next_step: int = 1

    async def emit(
        self,
        agent: str,
        action: str,
        status: str = "running",
        result: str = "",
        tool: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event: dict[str, Any] = {
            "workflow_id": self.workflow_id,
            "step": self.next_step,
            "agent": agent,
            "action": action,
            "status": status,
            "result": result,
            "timestamp": utc_now(),
        }
        if tool:
            event["tool"] = tool
        if parameters:
            event["parameters"] = parameters

        self.next_step += 1
        self.updated_at = event["timestamp"]
        self.steps.append(event)
        await self.queue.put(event)
        return event

    async def request_approval(
        self,
        tool: str,
        action: str,
        parameters: dict[str, Any],
    ) -> str:
        self.approval_event.clear()
        self.approval_result = "pending"
        self.pending_approval = {
            "tool": tool,
            "action": action,
            "parameters": parameters,
            "timestamp": utc_now(),
        }
        await self.emit(
            agent="Safety",
            action=action,
            status="waiting_approval",
            result="Human approval is required before this write action can continue.",
            tool=tool,
            parameters=parameters,
        )
        await self.approval_event.wait()
        decision = self.approval_result
        self.pending_approval = None
        self.approval_result = "pending"
        return decision

    async def finish(self, final_result: str, status: str = "complete") -> None:
        self.status = status
        self.final_result = final_result
        await self.emit(
            agent="Manager",
            action="Workflow complete" if status == "complete" else "Workflow failed",
            status=status,
            result=final_result,
        )
        await self.queue.put(None)


class WorkflowManager:
    """Simple process-local session store for demo workflows."""

    def __init__(self) -> None:
        self._sessions: dict[str, WorkflowSession] = {}
        self._lock = asyncio.Lock()

    async def create_session(self, user_input: str) -> WorkflowSession:
        async with self._lock:
            workflow_id = str(uuid4())
            session = WorkflowSession(workflow_id=workflow_id, user_input=user_input)
            self._sessions[workflow_id] = session
            return session

    def get_session(self, workflow_id: str) -> WorkflowSession | None:
        return self._sessions.get(workflow_id)

    async def submit_approval(self, workflow_id: str, decision: str) -> bool:
        session = self.get_session(workflow_id)
        if not session or not session.pending_approval:
            return False
        session.approval_result = decision
        session.approval_event.set()
        return True

    async def shutdown(self) -> None:
        for session in list(self._sessions.values()):
            if session.task and not session.task.done():
                session.task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await session.task


workflow_manager = WorkflowManager()

__all__ = ["WorkflowSession", "WorkflowManager", "workflow_manager", "utc_now"]
