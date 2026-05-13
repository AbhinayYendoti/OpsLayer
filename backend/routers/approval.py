"""Approval API routes."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from state.workflow_manager import workflow_manager

router = APIRouter(prefix="/api/workflow", tags=["approval"])


class ApprovalRequest(BaseModel):
    decision: Literal["approved", "rejected"]


class ApprovalResponse(BaseModel):
    success: bool


@router.post("/{workflow_id}/approve", response_model=ApprovalResponse)
async def approve_workflow(workflow_id: str, payload: ApprovalRequest) -> ApprovalResponse:
    success = await workflow_manager.submit_approval(workflow_id, payload.decision)
    if not success:
        raise HTTPException(status_code=404, detail="No pending approval found for workflow")
    return ApprovalResponse(success=True)


@router.post("/{workflow_id}/reject", response_model=ApprovalResponse)
async def reject_workflow(workflow_id: str) -> ApprovalResponse:
    success = await workflow_manager.submit_approval(workflow_id, "rejected")
    if not success:
        raise HTTPException(status_code=404, detail="No pending approval found for workflow")
    return ApprovalResponse(success=True)
