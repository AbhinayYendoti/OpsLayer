"""
libra_app/components/approval_modal.py
========================================
Human-in-the-loop approval modal.
Blocks workflow execution until user explicitly approves or rejects a write action.
This is the core safety mechanism — it cannot be bypassed.
"""

import reflex as rx
from libra_app.state.app_state import AppState


def approval_modal() -> rx.Component:
    """
    Approval modal dialog.
    Renders as a fixed overlay when AppState.show_approval_modal is True.
    The user MUST make a decision — cannot be dismissed by clicking outside.
    """
    return rx.cond(
        AppState.show_approval_modal,
        # Overlay + Modal
        rx.box(
            # Dark overlay
            rx.box(
                position="fixed",
                top="0",
                left="0",
                width="100vw",
                height="100vh",
                background="rgba(0, 0, 0, 0.75)",
                z_index="100",
                backdrop_filter="blur(4px)",
            ),
            # Modal card
            rx.box(
                rx.vstack(
                    # Header
                    rx.hstack(
                        rx.text("⚠️", font_size="1.5rem"),
                        rx.vstack(
                            rx.text(
                                "Action Requires Your Approval",
                                font_size="1.1rem",
                                font_weight="700",
                                color="#e5e5e5",
                            ),
                            rx.text(
                                "The AI agent wants to perform a write action.",
                                font_size="0.8rem",
                                color="#888888",
                            ),
                            spacing="0",
                            align_items="start",
                        ),
                        align="center",
                        spacing="3",
                    ),
                    rx.divider(border_color="#2a2a2a"),

                    # Action Type Badge
                    rx.hstack(
                        rx.text("ACTION:", font_size="0.75rem", color="#888888", font_weight="600"),
                        rx.badge(
                            AppState.pending_action_tool,
                            color_scheme="orange",
                            size="2",
                        ),
                        align="center",
                        spacing="2",
                    ),

                    # Action Description
                    rx.box(
                        rx.text(
                            "What will happen:",
                            font_size="0.75rem",
                            color="#888888",
                            font_weight="600",
                            margin_bottom="8px",
                        ),
                        rx.text(
                            AppState.pending_action_description,
                            font_size="0.9rem",
                            color="#e5e5e5",
                            line_height="1.6",
                        ),
                        background="#1a1a1a",
                        border="1px solid #2a2a2a",
                        border_radius="8px",
                        padding="14px",
                        width="100%",
                    ),

                    # Parameters Preview
                    rx.cond(
                        AppState.pending_action_params != "",
                        rx.box(
                            rx.text(
                                "Parameters:",
                                font_size="0.75rem",
                                color="#888888",
                                font_weight="600",
                                margin_bottom="8px",
                            ),
                            rx.text(
                                AppState.pending_action_params,
                                font_size="0.8rem",
                                color="#aaaaaa",
                                font_family="'JetBrains Mono', monospace",
                                white_space="pre-wrap",
                                word_break="break-all",
                            ),
                            background="#111111",
                            border="1px solid #222222",
                            border_radius="8px",
                            padding="12px",
                            width="100%",
                            max_height="150px",
                            overflow_y="auto",
                        ),
                        rx.box(),
                    ),

                    # Warning note
                    rx.hstack(
                        rx.text("ℹ️", font_size="0.8rem"),
                        rx.text(
                            "This action cannot be undone automatically. Review carefully.",
                            font_size="0.75rem",
                            color="#888888",
                        ),
                        align="center",
                        spacing="2",
                    ),

                    rx.divider(border_color="#2a2a2a"),

                    # Action Buttons
                    rx.hstack(
                        rx.button(
                            "❌  Reject",
                            on_click=AppState.reject_action,
                            background="transparent",
                            border="1px solid #3a3a3a",
                            color="#888888",
                            border_radius="8px",
                            padding="10px 20px",
                            cursor="pointer",
                            font_size="0.875rem",
                            _hover={"border_color": "#ef4444", "color": "#ef4444"},
                            transition="all 0.15s ease",
                        ),
                        rx.spacer(),
                        rx.button(
                            "✅  Approve",
                            on_click=AppState.approve_action,
                            background="#22c55e",
                            color="white",
                            border_radius="8px",
                            padding="10px 24px",
                            cursor="pointer",
                            font_size="0.875rem",
                            font_weight="600",
                            _hover={"background": "#16a34a", "transform": "translateY(-1px)"},
                            transition="all 0.15s ease",
                        ),
                        width="100%",
                        align="center",
                    ),

                    spacing="4",
                    padding="24px",
                ),
                background="#161616",
                border="1px solid #333333",
                border_radius="16px",
                max_width="480px",
                width="90vw",
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                z_index="101",
                box_shadow="0 25px 50px rgba(0,0,0,0.5)",
            ),
        ),
        rx.box(),  # Hidden when modal is not shown
    )
