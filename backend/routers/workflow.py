"""Workflow API routes."""

from __future__ import annotations

import asyncio
import json
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agents.orchestrator import run_workflow
from state.workflow_manager import workflow_manager

router = APIRouter(prefix="/api/workflow", tags=["workflow"])


class StartWorkflowRequest(BaseModel):
    input: str = Field(..., min_length=3, max_length=500)


class StartWorkflowResponse(BaseModel):
    workflow_id: str


class WorkflowResultResponse(BaseModel):
    final_result: str
    steps: list[dict]
    status: Literal["running", "complete", "error"]


@router.post("/start", response_model=StartWorkflowResponse)
async def start_workflow(payload: StartWorkflowRequest) -> StartWorkflowResponse:
    session = await workflow_manager.create_session(payload.input.strip())
    session.task = asyncio.create_task(run_workflow(session))
    return StartWorkflowResponse(workflow_id=session.workflow_id)


async def event_generator(workflow_id: str):
    session = workflow_manager.get_session(workflow_id)
    if not session:
        yield f"data: {json.dumps({'status': 'error', 'action': 'Workflow not found'})}\n\n"
        return

    while True:
        step = await session.queue.get()
        if step is None:
            break
        yield f"data: {json.dumps(step)}\n\n"
        await asyncio.sleep(0.1)


@router.get("/{workflow_id}/stream")
async def stream_workflow(workflow_id: str) -> StreamingResponse:
    if not workflow_manager.get_session(workflow_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
    return StreamingResponse(
        event_generator(workflow_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{workflow_id}/result", response_model=WorkflowResultResponse)
async def workflow_result(workflow_id: str) -> WorkflowResultResponse:
    session = workflow_manager.get_session(workflow_id)
    if not session:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResultResponse(
        final_result=session.final_result,
        steps=session.steps,
        status=session.status,  # type: ignore[arg-type]
    )
