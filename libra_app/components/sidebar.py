"""
libra_app/components/sidebar.py
================================
Notion-style sidebar navigation component.
Shows app branding, new workflow button, and session history.
"""

import reflex as rx
from libra_app.state.app_state import AppState, WorkflowRun


# ============================================================
# Color Constants
# ============================================================

SIDEBAR_BG = "#111111"
SIDEBAR_HOVER = "#1e1e1e"
SIDEBAR_BORDER = "#2a2a2a"
TEXT_PRIMARY = "#e5e5e5"
TEXT_SECONDARY = "#888888"
ACCENT = "#3b82f6"


# ============================================================
# Sub-components
# ============================================================

def logo() -> rx.Component:
    """App logo and name at the top of the sidebar."""
    return rx.hstack(
        rx.text("🤖", font_size="1.4rem"),
        rx.text(
            "Libra AI",
            font_weight="700",
            font_size="1.1rem",
            color=TEXT_PRIMARY,
            letter_spacing="-0.02em",
        ),
        rx.badge("DEMO", color_scheme="blue", size="1"),
        align="center",
        padding="20px 16px 16px 16px",
    )


def new_workflow_button() -> rx.Component:
    """Button to start a new workflow."""
    return rx.button(
        rx.hstack(
            rx.text("+", font_size="1.1rem"),
            rx.text("New Workflow"),
            align="center",
            spacing="2",
        ),
        on_click=AppState.reset_workflow,
        width="100%",
        background=ACCENT,
        color="white",
        border_radius="8px",
        padding="10px 14px",
        font_size="0.875rem",
        font_weight="500",
        cursor="pointer",
        margin="0 12px",
        width="calc(100% - 24px)",
        _hover={"background": "#2563eb", "transform": "translateY(-1px)"},
        transition="all 0.15s ease",
    )


def history_item(run: WorkflowRun) -> rx.Component:
    """Single history item in the sidebar."""
    status_icon = rx.cond(
        run.status == "complete",
        rx.text("✅", font_size="0.75rem"),
        rx.text("❌", font_size="0.75rem"),
    )

    return rx.hstack(
        status_icon,
        rx.vstack(
            rx.text(
                run.input_text,
                font_size="0.8rem",
                color=TEXT_PRIMARY,
                overflow="hidden",
                text_overflow="ellipsis",
                white_space="nowrap",
                max_width="160px",
            ),
            rx.text(
                run.created_at,
                font_size="0.7rem",
                color=TEXT_SECONDARY,
            ),
            spacing="0",
            align_items="start",
        ),
        padding="8px 16px",
        border_radius="6px",
        cursor="pointer",
        _hover={"background": SIDEBAR_HOVER},
        transition="background 0.1s",
        width="100%",
        overflow="hidden",
    )


def history_section() -> rx.Component:
    """Recent workflows section."""
    return rx.vstack(
        rx.text(
            "RECENT",
            font_size="0.65rem",
            font_weight="600",
            color=TEXT_SECONDARY,
            letter_spacing="0.08em",
            padding="8px 16px 4px 16px",
        ),
        rx.cond(
            AppState.workflow_history.length() > 0,
            rx.vstack(
                rx.foreach(AppState.workflow_history, history_item),
                spacing="0",
                width="100%",
            ),
            rx.text(
                "No workflows yet",
                font_size="0.8rem",
                color=TEXT_SECONDARY,
                padding="8px 16px",
            ),
        ),
        spacing="0",
        width="100%",
    )


def sidebar_footer() -> rx.Component:
    """Bottom of sidebar — settings/docs links."""
    return rx.vstack(
        rx.divider(border_color=SIDEBAR_BORDER),
        rx.vstack(
            rx.hstack(
                rx.text("⚙", font_size="0.9rem"),
                rx.text("Settings", font_size="0.85rem", color=TEXT_SECONDARY),
                padding="8px 16px",
                cursor="pointer",
                width="100%",
                border_radius="6px",
                _hover={"background": SIDEBAR_HOVER, "color": TEXT_PRIMARY},
            ),
            rx.hstack(
                rx.text("📖", font_size="0.9rem"),
                rx.text("Documentation", font_size="0.85rem", color=TEXT_SECONDARY),
                padding="8px 16px",
                cursor="pointer",
                width="100%",
                border_radius="6px",
                _hover={"background": SIDEBAR_HOVER, "color": TEXT_PRIMARY},
            ),
            spacing="0",
        ),
        spacing="1",
        width="100%",
        padding_bottom="8px",
    )


# ============================================================
# Main Sidebar Component
# ============================================================

def sidebar() -> rx.Component:
    """Full sidebar component."""
    return rx.vstack(
        logo(),
        rx.box(height="8px"),
        new_workflow_button(),
        rx.box(height="16px"),
        rx.divider(border_color=SIDEBAR_BORDER),
        history_section(),
        rx.spacer(),
        sidebar_footer(),
        background=SIDEBAR_BG,
        border_right=f"1px solid {SIDEBAR_BORDER}",
        min_width="240px",
        width="240px",
        height="100vh",
        position="fixed",
        left="0",
        top="0",
        overflow_y="auto",
        spacing="0",
        align_items="start",
    )
