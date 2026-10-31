"""Reusable Gradio components and layout for the screening dashboard."""

from __future__ import annotations

from html import escape
from pathlib import Path

import gradio as gr
import numpy as np
from PIL import Image

from .config import CLASS_LABELS, MODEL_PATH, REFERABLE_THRESHOLD
from .gradcam import predict_and_generate_gradcam
from .predictor import prediction_from_probabilities
from .preprocessing import preprocess_fundus
from .quality_check import check_image_quality


def _quality_card(result: dict) -> str:
    passed = result["status"] == "PASS"
    status = "PASS" if passed else "FAIL"
    style = "pass" if passed else "fail"
    metrics = []
    if result.get("width") is not None:
        metrics.extend([
            ("Resolution", f"{result['width']} x {result['height']} px"),
            ("Blur detail", f"{result['blur_score']:.2f}"),
            ("Mean brightness", f"{result['mean_brightness']:.2f}"),
            ("Contrast", f"{result['contrast_std']:.2f}"),
            ("Visible pixels", f"{result['non_dark_ratio']:.1%}"),
            ("Retinal field", f"{result['retinal_field_ratio']:.1%}"),
        ])
    metrics_html = "".join(
        f"<div class='quality-metric'><span>{escape(label)}</span><b>{escape(value)}</b></div>"
        for label, value in metrics
    )
    reasons = "".join(f"<li>{escape(str(reason))}</li>" for reason in result["reasons"])
    instruction = (
        "Quality checks passed. These image heuristics do not validate clinical suitability."
        if passed else "Prediction was skipped. Please use a clear, well-lit retinal image and try again."
    )
    return (
        f"<section class='quality-card'><div class='quality-title {style}'>"
        f"<span aria-hidden='true'>{'&#10003;' if passed else '&#9888;'}</span> Image quality: {status}</div>"
        f"<div class='quality-metrics'>{metrics_html}</div><ul class='quality-message'>{reasons}</ul>"
        f"<p class='quality-message'>{escape(instruction)}</p></section>"
    )


def _screening_card(prediction: dict) -> str:
    referable = prediction["binary_label"] == "Referable DR"
    kind = "referable" if referable else "nonreferable"
    binary = "REFERABLE DR" if referable else "NON-REFERABLE DR"
    return (
        f"<section class='screening-card {kind}'><div class='screening-eyebrow'>Primary screening estimate</div>"
        f"<div class='screening-title'>{binary}</div>"
        "<div class='screening-meta'>"
        f"<div><span>Predicted severity</span><b>Grade {prediction['grade']} - {escape(prediction['grade_label'])}</b></div>"
        f"<div><span>Referable probability</span><b>{prediction['referable_probability']:.1%}</b></div>"
        f"<div><span>Configured threshold</span><b>{prediction['binary_threshold']:.0%}</b></div>"
        "<div><span>Referral mapping</span><b>Grades 2-4</b></div></div>"
        "<p class='screening-note'>Probability is a model output, not clinical certainty. The configured threshold follows the project's initial evaluation setting and is not clinically optimized.</p></section>"
    )


def _probability_chart(prediction: dict) -> str:
    values = prediction["probabilities"]
    total = float(np.sum(values))
    rows = []
    for grade, (label, probability) in enumerate(zip(CLASS_LABELS, values)):
        predicted = grade == prediction["grade"]
        pct = float(probability) * 100
        rows.append(
            f"<div class='probability-row{' predicted' if predicted else ''}'>"
            f"<div class='probability-label'>Grade {grade} - {escape(label)}{' <b>Predicted</b>' if predicted else ''}</div>"
            f"<div class='probability-track'><div class='probability-fill' style='width:{min(max(pct, 0), 100):.2f}%'></div></div>"
            f"<div class='probability-value'>{pct:.1f}%</div></div>"
        )
    return (
        "<section class='probability-card'><div class='probability-heading'>"
        "<strong>DR Severity Distribution</strong><span>Model probabilities</span></div>"
        + "".join(rows)
        + f"<div class='probability-total'>Total: {total:.1%}</div></section>"
    )


def _empty_quality() -> str:
    return "<section class='quality-card'><div class='section-caption'>Quality assessment will appear here after analysis.</div></section>"


def _empty_result() -> str:
    return (
        "<section class='screening-card'><div class='screening-eyebrow'>Screening result</div>"
        "<div class='screening-title'>Ready for analysis</div>"
        "<p class='screening-note'>Upload a retinal fundus image, then run the model to see its screening estimate and class probabilities.</p></section>"
    )


def build_screening_ui(model, model_startup_error: str | None) -> gr.Blocks:
    """Build the dashboard while receiving the already initialized model."""

    def analyze_image(image_path: str | None, progress=gr.Progress()):
        if not image_path:
            return _empty_quality(), _empty_result(), "", None, None, None, None
        path = Path(image_path)
        try:
            with Image.open(path) as image:
                original = np.asarray(image.convert("RGB").copy())
        except Exception as exc:
            error = f"Could not open this image: {escape(str(exc))}"
            return _quality_card({"status": "FAIL", "reasons": ["Image file could not be opened."], "width": None}), error, "", None, None, None, None

        progress(0.08, desc="Checking image quality")
        quality = check_image_quality(path)
        quality_html = _quality_card(quality)
        if quality["status"] != "PASS":
            return quality_html, (
                "<section class='screening-card failed'><div class='screening-eyebrow'>Screening result</div>"
                "<div class='screening-title'>Analysis paused</div><p class='screening-note'>The image did not pass the project's quality checks, so no model prediction was made.</p></section>"
            ), "", original, None, None, None
        if model is None:
            return quality_html, (
                f"<section class='screening-card failed'><div class='screening-title'>Model unavailable</div>"
                f"<p class='screening-note'>{escape(model_startup_error or 'Model weights could not be loaded.')}</p>"
                f"<p class='screening-note'>Expected checkpoint: {escape(str(MODEL_PATH))}</p></section>"
            ), "", original, None, None, None

        try:
            progress(0.25, desc="Preparing retinal image")
            prepared = preprocess_fundus(path)
            progress(0.45, desc="Running ResNet50 and Grad-CAM")
            scores, heatmap, overlay = predict_and_generate_gradcam(model, prepared)
            prediction = prediction_from_probabilities(scores, REFERABLE_THRESHOLD)
            progress(1.0, desc="Analysis complete")
            return (
                quality_html,
                _screening_card(prediction),
                _probability_chart(prediction),
                original,
                prepared.display_rgb,
                heatmap,
                overlay,
            )
        except Exception as exc:
            error = escape(str(exc))
            return quality_html, (
                f"<section class='screening-card failed'><div class='screening-title'>Analysis failed</div>"
                f"<p class='screening-note'>{error}</p></section>"
            ), "", original, None, None, None

    def reset_results(image_path):
        return (
            gr.update(interactive=bool(image_path)),
            _empty_quality(),
            _empty_result(),
            "",
            None,
            None,
            None,
            None,
        )

    def clear_upload():
        return (None, *reset_results(None))

    with gr.Blocks(title="AI_DR | Diabetic Retinopathy Screening") as demo:
        with gr.Column(elem_classes="app-shell"):
            gr.HTML(
                "<header class='topbar'><div class='brand'><div class='brand-mark' aria-hidden='true'>"
                "<svg width='25' height='25' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'>"
                "<path d='M2.5 12s3.4-6.5 9.5-6.5 9.5 6.5 9.5 6.5-3.4 6.5-9.5 6.5S2.5 12 2.5 12Z' stroke='currentColor' stroke-width='1.7'/>"
                "<circle cx='12' cy='12' r='3.1' stroke='currentColor' stroke-width='1.7'/><circle cx='12' cy='12' r='1' fill='currentColor'/></svg>"
                "</div><div><div class='brand-name'>AI_DR</div><div class='brand-subtitle'>Diabetic Retinopathy Screening System</div></div></div>"
                "<div class='topbar-right'><nav class='nav-links' aria-label='Main navigation'>"
                "<a href='#screening'>Screening</a><a href='#about'>About</a><a href='#methodology'>Methodology</a></nav>"
                "<span class='prototype-badge'>RESEARCH PROTOTYPE</span></div></header>"
            )
            gr.HTML(
                "<section class='hero-card'><h1 class='hero-title'>AI-Powered Retinal Screening</h1>"
                "<p class='hero-description'>Analyze retinal fundus images, assess image quality, identify referable diabetic retinopathy, and visualize model attention.</p>"
                "<span class='model-badge'>ResNet50&nbsp; | &nbsp;Five-Class Classification</span></section>"
            )
            if model_startup_error:
                gr.HTML(
                    f"<div class='error-banner'><strong>Model could not be loaded.</strong> {escape(model_startup_error)}<br>Expected weights: {escape(str(MODEL_PATH))}</div>"
                )

            with gr.Row(elem_id="screening", equal_height=False):
                with gr.Column(scale=5, min_width=320, elem_classes="section-card upload-panel"):
                    gr.Markdown("### Upload Fundus Image", elem_classes="section-heading")
                    gr.Markdown("Choose a clear retinal image. Supported formats: JPG, JPEG, PNG, BMP, TIFF.", elem_classes="section-caption")
                    image_input = gr.Image(
                        label="Drop a fundus image here or browse", type="filepath",
                        sources=["upload"], height=300, buttons=["fullscreen"],
                    )
                    with gr.Row():
                        analyze_button = gr.Button("Analyze Image", variant="primary", interactive=False, elem_classes="analyze-button", scale=3)
                        clear_button = gr.Button("Clear", variant="secondary", elem_classes="clear-button", scale=1)
                    quality_output = gr.HTML(_empty_quality())
                with gr.Column(scale=7, min_width=350, elem_classes="section-card results-panel"):
                    gr.Markdown("### Screening Results", elem_classes="section-heading")
                    gr.Markdown("Predictions are model estimates for research review.", elem_classes="section-caption")
                    result_output = gr.HTML(_empty_result())
                    probability_output = gr.HTML()

            gr.Markdown("### Image Analysis & Explainability", elem_classes="section-heading")
            gr.Markdown(
                "Grad-CAM highlights image regions that influenced the model's prediction. It is an interpretability visualization, not a clinical lesion segmentation.",
                elem_classes="viewer-caption",
            )
            with gr.Row(equal_height=False):
                with gr.Column(scale=1, min_width=280, elem_classes="viewer-panel"):
                    original_output = gr.Image(label="Original fundus image", type="numpy", height=300, buttons=["fullscreen"])
                with gr.Column(scale=1, min_width=280, elem_classes="viewer-panel"):
                    processed_output = gr.Image(label="Preprocessed fundus image", type="numpy", height=300, buttons=["fullscreen"])
            with gr.Row(equal_height=False):
                with gr.Column(scale=1, min_width=280, elem_classes="viewer-panel"):
                    heatmap_output = gr.Image(label="Grad-CAM heatmap", type="numpy", height=300, buttons=["fullscreen"])
                with gr.Column(scale=1, min_width=280, elem_classes="viewer-panel"):
                    overlay_output = gr.Image(label="Grad-CAM overlay", type="numpy", height=300, buttons=["fullscreen"])

            with gr.Accordion("About the AI Model", open=False, elem_id="about", elem_classes="method-panel"):
                gr.HTML(
                    "<div class='method-copy'><p><strong>Architecture:</strong> ResNet50 with a five-class softmax head.</p>"
                    "<p><strong>Task:</strong> Grades 0-4: No DR, Mild, Moderate, Severe, and Proliferative DR.</p>"
                    "<p><strong>Binary screening:</strong> Grades 0-1 map to Non-referable; grades 2-4 map to Referable. The displayed referral probability sums the probabilities for grades 2, 3, and 4.</p>"
                    "<p><strong>Preprocessing:</strong> LAB lightness CLAHE, Gaussian filtering, dark border crop, 512px aspect-preserving resize/padding, the training RGB statistics/JPEG export step, then 224px resize and ResNet50 preprocessing.</p>"
                    "<p><strong>Explainability:</strong> Grad-CAM uses the ResNet50 <code>conv5_block3_out</code> feature layer.</p></div>"
                )
            with gr.Accordion("Methodology and multilingual explanation", open=False, elem_id="methodology", elem_classes="method-panel"):
                gr.Markdown("The research threshold is configurable and is not clinically optimized. Quality checks are image heuristics, not a medical validation step.", elem_classes="method-copy")
                gr.Markdown("#### Multilingual explanation (planned)")
                with gr.Row():
                    gr.Dropdown(choices=["English", "Hindi", "Telugu", "Tamil", "Kannada", "Bengali"], value="English", label="Explanation language", scale=1)
                    gr.Button("Generate explanation", interactive=False, scale=1)
                gr.Textbox(label="LLM explanation", value="This interface will be connected after an LLM provider and API key are configured.", lines=3, interactive=False)

            gr.HTML(
                "<footer class='research-footer'><strong>Research-use disclaimer:</strong> This application is an academic research prototype and is not clinically validated. Its predictions must not be used as a substitute for professional medical examination or diagnosis.</footer>"
            )

        outputs = [analyze_button, quality_output, result_output, probability_output,
                   original_output, processed_output, heatmap_output, overlay_output]
        image_input.change(reset_results, inputs=image_input, outputs=outputs, queue=False)
        clear_button.click(clear_upload, outputs=[image_input, *outputs], queue=False)
        analyze_button.click(
            analyze_image,
            inputs=image_input,
            outputs=outputs[1:],
            concurrency_limit=1,
            show_progress="full",
            scroll_to_output=True,
        )
    return demo

