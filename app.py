"""Entry point for the AI_DR screening dashboard."""

from __future__ import annotations

import gradio as gr

from src.predictor import load_model
from src.ui_components import build_screening_ui
from src.ui_styles import CUSTOM_CSS


try:
    # Load the trained checkpoint once when the application starts.
    MODEL = load_model()
    MODEL_STARTUP_ERROR = None
except Exception as exc:
    # Keep the dashboard available so it can show the missing/incompatible model message.
    MODEL = None
    MODEL_STARTUP_ERROR = str(exc)


demo = build_screening_ui(MODEL, MODEL_STARTUP_ERROR)


if __name__ == "__main__":
    demo.queue(default_concurrency_limit=1).launch(
        theme=gr.themes.Soft(primary_hue="teal", secondary_hue="slate"),
        css=CUSTOM_CSS,
    )
