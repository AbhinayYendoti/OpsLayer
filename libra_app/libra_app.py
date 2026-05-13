"""
libra_app/libra_app.py
========================
Main Reflex application entry point for Libra AI Coworker Demo.
Composes all components into the full Notion-style layout.
"""

import reflex as rx
from libra_app.state.app_state import AppState
from libra_app.components.sidebar import sidebar
from libra_app.components.workflow_log import workflow_log
from libra_app.components.approval_modal import approval_modal
from libra_app.components.result_card import result_card


# ============================================================
# Demo Workflow Presets (Quick-start buttons)
# ============================================================

DEMO_WORKFLOWS = [
    {
        "icon": "📧",
        "label": "CRM Update",
        "prompt": "Search my Gmail for emails from Acme Corp this week and add a CRM note summarizing their status.",
    },
    {
        "icon": "💬",
        "label": "Slack Digest",
        "prompt": "Summarize today's messages in the #sales channel and give me the key highlights.",
    },
    {
        "icon": "🎯",
        "label": "Lead Research",
        "prompt": "Research TechCorp in my Gmail and Slack, then prepare a CRM note and draft a follow-up email.",
    },
]


# ============================================================
# Workflow Input Panel
# ============================================================

def demo_button(workflow: dict) -> rx.Component:
    """A quick-start demo workflow button."""
    return rx.button(
        rx.hstack(
            rx.text(workflow["icon"], font_size="0.9rem"),
            rx.text(workflow["label"], font_size="0.8rem"),
            align="center",
            spacing="1",
        ),
        on_click=AppState.set_input(workflow["prompt"]),
        background="#1a1a1a",
        border="1px solid #2a2a2a",
        color="#aaaaaa",
        border_radius="8px",
        padding="6px 12px",
        cursor="pointer",
        font_size="0.8rem",
        _hover={"border_color": "#3b82f6", "color": "#e5e5e5", "background": "#1e1e1e"},
        transition="all 0.15s ease",
    )


def workflow_input_panel() -> rx.Component:
    """Main input area where the user enters their workflow request."""
    return rx.vstack(
        # Title
        rx.vstack(
            rx.text(
                "What should I do?",
                font_size="1.5rem",
                font_weight="700",
                color="#e5e5e5",
                letter_spacing="-0.02em",
            ),
            rx.text(
                "Describe a multi-step workflow and I'll research, analyze, and execute it for you.",
                font_size="0.875rem",
                color="#888888",
            ),
            spacing="1",
            align_items="start",
        ),

        # Quick demo buttons
        rx.hstack(
            rx.text("Quick start:", font_size="0.75rem", color="#666666"),
            *[demo_button(w) for w in DEMO_WORKFLOWS],
            align="center",
            spacing="2",
            flex_wrap="wrap",
        ),

        # Text input
        rx.text_area(
            value=AppState.current_input,
            on_change=AppState.set_input,
            placeholder="e.g. 'Find emails from Acme Corp this week and update the CRM with a summary...'",
            min_height="100px",
            background="#1a1a1a",
            border="1px solid #2a2a2a",
            border_radius="10px",
            color="#e5e5e5",
            font_size="0.9rem",
            padding="14px",
            resize="vertical",
            _focus={"border_color": "#3b82f6", "outline": "none"},
            _placeholder={"color": "#555555"},
            width="100%",
        ),

        # Run button + status
        rx.hstack(
            rx.cond(
                AppState.is_loading,
                rx.hstack(
                    rx.spinner(size="2", color="blue"),
                    rx.text(
                        "Running workflow...",
                        font_size="0.875rem",
                        color="#888888",
                    ),
                    align="center",
                    spacing="2",
                ),
                rx.text(
                    f"{AppState.current_input.length()} / 500 chars",
                    font_size="0.75rem",
                    color="#555555",
                ),
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.cond(
                        AppState.is_loading,
                        rx.spinner(size="1"),
                        rx.text("▶", font_size="0.9rem"),
                    ),
                    rx.text(
                        rx.cond(AppState.is_loading, "Running...", "Run Workflow"),
                    ),
                    align="center",
                    spacing="2",
                ),
                on_click=AppState.run_workflow,
                is_disabled=rx.cond(
                    AppState.is_loading | (AppState.current_input == ""),
                    True,
                    False,
                ),
                background=rx.cond(
                    AppState.is_loading | (AppState.current_input == ""),
                    "#1e1e1e",
                    "#3b82f6",
                ),
                color=rx.cond(
                    AppState.is_loading | (AppState.current_input == ""),
                    "#555555",
                    "white",
                ),
                border_radius="8px",
                padding="10px 20px",
                cursor=rx.cond(
                    AppState.is_loading | (AppState.current_input == ""),
                    "not-allowed",
                    "pointer",
                ),
                font_weight="600",
                font_size="0.875rem",
                _hover={},
                transition="all 0.15s ease",
            ),
            align="center",
            width="100%",
        ),

        spacing="4",
        align_items="start",
        background="#161616",
        border="1px solid #2a2a2a",
        border_radius="12px",
        padding="24px",
        width="100%",
    )


# ============================================================
# Main Page Layout
# ============================================================

def index() -> rx.Component:
    """Main page — full layout with sidebar and content area."""
    return rx.box(
        # Sidebar (fixed left)
        sidebar(),

        # Main content area (offset by sidebar width)
        rx.box(
            rx.vstack(
                # Page header
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "AI Coworker",
                            font_size="1.8rem",
                            font_weight="800",
                            color="#e5e5e5",
                            letter_spacing="-0.03em",
                        ),
                        rx.text(
                            "Multi-agent workflow automation • Powered by CrewAI + OpenAI",
                            font_size="0.825rem",
                            color="#666666",
                        ),
                        spacing="0",
                        align_items="start",
                    ),
                    rx.badge(
                        "v1.0 Demo",
                        color_scheme="gray",
                        size="1",
                        margin_top="8px",
                    ),
                    justify="between",
                    align="start",
                    width="100%",
                ),

                # Input panel
                workflow_input_panel(),

                # Live workflow log
                workflow_log(),

                # Final result card
                result_card(),

                spacing="6",
                padding="32px",
                max_width="860px",
                margin="0 auto",
                align_items="start",
                width="100%",
            ),
            margin_left="240px",  # Offset for fixed sidebar
            min_height="100vh",
            background="#111111",
            width="calc(100% - 240px)",
        ),

        # Approval modal (always rendered, hidden by default)
        approval_modal(),

        background="#111111",
        font_family="'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
        min_height="100vh",
    )


# ============================================================
# App Configuration
# ============================================================

app = rx.App(
    style={
        "background": "#111111",
        "color": "#e5e5e5",
        "font_family": "Inter, -apple-system, sans-serif",
    },
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
    ],
)

app.add_page(index, route="/", title="Libra AI Coworker")
