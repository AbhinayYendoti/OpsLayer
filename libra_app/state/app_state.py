"""
libra_app/state/app_state.py
============================
Central Reflex state for the Libra AI Coworker Demo.
All UI components read from and write to this state.
"""

import reflex as rx
from typing import List
from datetime import datetime
import asyncio


# ============================================================
# Data Models (rx.Base for Reflex serialization)
# ============================================================

class WorkflowStep(rx.Base):
    """Represents a single step in the workflow execution log."""
    step_number: int = 0
    agent: str = ""           # "Researcher" | "Analyst" | "Executor" | "Manager"
    action: str = ""          # Human-readable description of the action
    result: str = ""          # Output/result from this step
    status: str = "running"   # "running" | "done" | "error" | "waiting_approval"
    timestamp: str = ""


class WorkflowRun(rx.Base):
    """Represents a completed workflow run stored in history."""
    id: str = ""
    input_text: str = ""
    step_count: int = 0
    final_result: str = ""
    status: str = "complete"  # "complete" | "failed" | "cancelled"
    created_at: str = ""


# ============================================================
# Main App State
# ============================================================

class AppState(rx.State):
    """
    Global application state.
    Reflex automatically syncs this state to the frontend via websockets.
    """

    # --- Current Workflow ---
    current_input: str = ""
    current_steps: List[WorkflowStep] = []
    current_status: str = "idle"  # "idle" | "running" | "complete" | "error"
    final_result: str = ""
    error_message: str = ""

    # --- UI State ---
    is_loading: bool = False

    # --- Session History (shown in sidebar) ---
    workflow_history: List[WorkflowRun] = []

    # --- Approval State ---
    show_approval_modal: bool = False
    pending_action_description: str = ""
    pending_action_tool: str = ""
    pending_action_params: str = ""  # JSON string of params
    approval_result: str = "pending"  # "pending" | "approved" | "rejected"

    # --------------------------------------------------------
    # Input Handlers
    # --------------------------------------------------------

    def set_input(self, value: str):
        """Update the workflow input text."""
        self.current_input = value

    # --------------------------------------------------------
    # Workflow Lifecycle
    # --------------------------------------------------------

    async def run_workflow(self):
        """
        Main entry point: triggered when user clicks 'Run Workflow'.
        Kicks off the CrewAI orchestration in a background thread.
        """
        if not self.current_input.strip():
            self.error_message = "Please enter a workflow description."
            return

        # Reset state for new run
        self.is_loading = True
        self.current_status = "running"
        self.current_steps = []
        self.final_result = ""
        self.error_message = ""

        # Import here to avoid circular imports
        from libra_app.agents.orchestrator import run_crew

        try:
            # Run the crew (this will call add_step() as it progresses)
            result = await asyncio.to_thread(
                run_crew,
                self.current_input,
                self,  # Pass state for callbacks
            )
            self.final_result = result
            self.current_status = "complete"

            # Save to history
            self._save_to_history()

        except Exception as e:
            self.error_message = f"Workflow failed: {str(e)}"
            self.current_status = "error"
        finally:
            self.is_loading = False

    def reset_workflow(self):
        """Clear the current workflow and start fresh."""
        self.current_input = ""
        self.current_steps = []
        self.current_status = "idle"
        self.final_result = ""
        self.error_message = ""
        self.show_approval_modal = False

    def _save_to_history(self):
        """Save the current completed workflow to session history."""
        run = WorkflowRun(
            id=f"run_{len(self.workflow_history) + 1}",
            input_text=self.current_input[:60] + ("..." if len(self.current_input) > 60 else ""),
            step_count=len(self.current_steps),
            final_result=self.final_result[:200],
            status="complete" if self.current_status == "complete" else "failed",
            created_at=datetime.now().strftime("%b %d, %H:%M"),
        )
        self.workflow_history.insert(0, run)  # Most recent first

    # --------------------------------------------------------
    # Step Logging (called by agents during execution)
    # --------------------------------------------------------

    def add_step(self, agent: str, action: str, status: str = "running"):
        """Add a new step to the live workflow log."""
        step = WorkflowStep(
            step_number=len(self.current_steps) + 1,
            agent=agent,
            action=action,
            status=status,
            timestamp=datetime.now().strftime("%H:%M:%S"),
        )
        self.current_steps.append(step)

    def update_last_step(self, result: str, status: str = "done"):
        """Update the most recent step with its result."""
        if self.current_steps:
            last = self.current_steps[-1]
            last.result = result
            last.status = status
            # Reflex requires reassignment to trigger reactivity
            self.current_steps = self.current_steps

    # --------------------------------------------------------
    # Approval Flow
    # --------------------------------------------------------

    def request_approval(self, tool: str, description: str, params_json: str):
        """
        Called by executor agent before a write operation.
        Pauses the UI and shows the approval modal.
        """
        self.pending_action_tool = tool
        self.pending_action_description = description
        self.pending_action_params = params_json
        self.approval_result = "pending"
        self.show_approval_modal = True

    def approve_action(self):
        """User approved the pending action."""
        self.approval_result = "approved"
        self.show_approval_modal = False
        self.add_step("Safety", f"✅ User approved: {self.pending_action_tool}", "done")

    def reject_action(self):
        """User rejected the pending action."""
        self.approval_result = "rejected"
        self.show_approval_modal = False
        self.add_step("Safety", f"❌ User rejected: {self.pending_action_tool}", "done")
