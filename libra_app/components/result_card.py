"""
libra_app/components/result_card.py
=====================================
Final result card shown when a workflow completes successfully.
Renders the agent's final output with copy functionality.
"""

import reflex as rx
from libra_app.state.app_state import AppState


def result_card() -> rx.Component:
    """
    Result card — only shown when current_status == 'complete'.
    Displays the final workflow output with action buttons.
    """
    return rx.cond(
        AppState.current_status == "complete",
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.hstack(
                        rx.text("✅", font_size="1.1rem"),
                        rx.text(
                            "Workflow Complete",
                            font_size="1rem",
                            font_weight="700",
                            color="#e5e5e5",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    rx.badge("SUCCESS", color_scheme="green", size="1"),
                    justify="between",
                    align="center",
                    width="100%",
                ),
                rx.divider(border_color="#2a2a2a"),

                # Result Content
                rx.box(
                    rx.markdown(
                        AppState.final_result,
                        color="#e5e5e5",
                        font_size="0.9rem",
                        line_height="1.7",
                    ),
                    background="#111111",
                    border="1px solid #2a2a2a",
                    border_radius="8px",
                    padding="16px",
                    width="100%",
                    max_height="400px",
                    overflow_y="auto",
                ),

                # Action Buttons
                rx.hstack(
                    rx.button(
                        "🔄  Run Again",
                        on_click=AppState.reset_workflow,
                        background="transparent",
                        border="1px solid #3a3a3a",
                        color="#888888",
                        border_radius="8px",
                        padding="8px 16px",
                        cursor="pointer",
                        font_size="0.8rem",
                        _hover={"border_color": "#3b82f6", "color": "#3b82f6"},
                        transition="all 0.15s ease",
                    ),
                    spacing="2",
                ),

                spacing="4",
                padding="20px",
            ),
            background="#161616",
            border="1px solid #22c55e44",
            border_radius="12px",
            width="100%",
            margin_top="16px",
        ),
        rx.box(),
    )
