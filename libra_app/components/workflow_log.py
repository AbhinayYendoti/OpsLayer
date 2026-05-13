"""
libra_app/components/workflow_log.py
=====================================
Live workflow step log component.
Shows real-time agent activity as the workflow executes.
"""

import reflex as rx
from libra_app.state.app_state import AppState, WorkflowStep


# ============================================================
# Agent Color Mapping
# ============================================================

AGENT_COLORS = {
    "Manager": "#22c55e",
    "Researcher": "#3b82f6",
    "Analyst": "#8b5cf6",
    "Executor": "#f97316",
    "Safety": "#ef4444",
}

STATUS_ICONS = {
    "running": "🔄",
    "done": "✅",
    "error": "❌",
    "waiting_approval": "⏳",
}


# ============================================================
# Individual Step Card
# ============================================================

def agent_badge(agent_name: str) -> rx.Component:
    """Colored badge showing which agent performed this step."""
    # Use a default color for unknown agents
    return rx.badge(
        agent_name,
        color_scheme=rx.cond(
            agent_name == "Researcher", "blue",
            rx.cond(
                agent_name == "Analyst", "violet",
                rx.cond(
                    agent_name == "Executor", "orange",
                    rx.cond(
                        agent_name == "Safety", "red",
                        "green",  # Manager and default
                    ),
                ),
            ),
        ),
        size="1",
        radius="full",
    )


def step_status_icon(status: str) -> rx.Component:
    """Icon showing the step status."""
    return rx.cond(
        status == "done",
        rx.text("✅", font_size="1rem"),
        rx.cond(
            status == "error",
            rx.text("❌", font_size="1rem"),
            rx.cond(
                status == "waiting_approval",
                rx.text("⏳", font_size="1rem"),
                # Default: running spinner
                rx.spinner(size="1", color="blue"),
            ),
        ),
    )


def step_card(step: WorkflowStep) -> rx.Component:
    """Card displaying a single workflow step."""
    return rx.box(
        rx.hstack(
            # Step number
            rx.box(
                rx.text(
                    step.step_number,
                    font_size="0.7rem",
                    color="#888888",
                    font_weight="600",
                ),
                min_width="20px",
                text_align="center",
            ),
            # Status icon
            step_status_icon(step.status),
            # Content
            rx.vstack(
                rx.hstack(
                    agent_badge(step.agent),
                    rx.text(
                        step.timestamp,
                        font_size="0.7rem",
                        color="#666666",
                    ),
                    align="center",
                    spacing="2",
                ),
                rx.text(
                    step.action,
                    font_size="0.875rem",
                    color="#e5e5e5",
                    line_height="1.5",
                ),
                # Result (expandable, shown when available)
                rx.cond(
                    step.result != "",
                    rx.box(
                        rx.text(
                            step.result,
                            font_size="0.8rem",
                            color="#aaaaaa",
                            font_family="'JetBrains Mono', monospace",
                            white_space="pre-wrap",
                            overflow="hidden",
                            max_height="120px",
                        ),
                        background="#1a1a1a",
                        border="1px solid #2a2a2a",
                        border_radius="6px",
                        padding="10px",
                        margin_top="4px",
                    ),
                    rx.box(),
                ),
                spacing="1",
                align_items="start",
                flex="1",
            ),
            align="start",
            spacing="3",
            width="100%",
        ),
        padding="14px 16px",
        border_bottom="1px solid #1e1e1e",
        _hover={"background": "#141414"},
        transition="background 0.1s",
    )


# ============================================================
# Empty State
# ============================================================

def empty_state() -> rx.Component:
    """Shown when no workflow is running."""
    return rx.vstack(
        rx.text("⚡", font_size="2.5rem"),
        rx.text(
            "Ready to work",
            font_size="1.1rem",
            font_weight="600",
            color="#e5e5e5",
        ),
        rx.text(
            "Enter a workflow above and click Run to get started.",
            font_size="0.875rem",
            color="#888888",
            text_align="center",
        ),
        spacing="2",
        align="center",
        padding="48px 24px",
    )


# ============================================================
# Main Workflow Log Component
# ============================================================

def workflow_log() -> rx.Component:
    """
    Live workflow log showing all agent steps.
    Updates reactively as AppState.current_steps changes.
    """
    return rx.box(
        # Header
        rx.hstack(
            rx.text(
                "Live Workflow Log",
                font_size="0.875rem",
                font_weight="600",
                color="#e5e5e5",
            ),
            # Step counter badge
            rx.cond(
                AppState.current_steps.length() > 0,
                rx.badge(
                    AppState.current_steps.length(),
                    color_scheme="gray",
                    size="1",
                ),
                rx.box(),
            ),
            # Status badge
            rx.cond(
                AppState.current_status == "running",
                rx.badge("● RUNNING", color_scheme="blue", size="1"),
                rx.cond(
                    AppState.current_status == "complete",
                    rx.badge("✓ COMPLETE", color_scheme="green", size="1"),
                    rx.cond(
                        AppState.current_status == "error",
                        rx.badge("✗ ERROR", color_scheme="red", size="1"),
                        rx.box(),
                    ),
                ),
            ),
            justify="between",
            align="center",
            padding="16px 20px 12px 20px",
            border_bottom="1px solid #2a2a2a",
        ),
        # Steps list
        rx.cond(
            AppState.current_steps.length() > 0,
            rx.vstack(
                rx.foreach(AppState.current_steps, step_card),
                spacing="0",
                width="100%",
            ),
            empty_state(),
        ),
        # Error message
        rx.cond(
            AppState.error_message != "",
            rx.box(
                rx.text(
                    f"⚠️ {AppState.error_message}",
                    color="#ef4444",
                    font_size="0.875rem",
                ),
                background="#1f0a0a",
                border="1px solid #7f1d1d",
                border_radius="8px",
                padding="12px 16px",
                margin="12px",
            ),
            rx.box(),
        ),
        background="#161616",
        border="1px solid #2a2a2a",
        border_radius="12px",
        overflow="hidden",
        width="100%",
    )
