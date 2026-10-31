"""Grad-CAM for the nested ResNet50 backbone."""

from __future__ import annotations

import cv2
import numpy as np
import tensorflow as tf

from .config import MODEL_INPUT_SIZE
from .preprocessing import PreparedImage


def _run_gradcam(model: tf.keras.Model, prepared: PreparedImage,
                 class_index: int | None = None):
    """Run model scores and Grad-CAM from one differentiable forward pass."""
    backbone = model.get_layer("resnet50")
    last_conv = backbone.get_layer("conv5_block3_out")
    feature_model = tf.keras.Model(backbone.inputs, [last_conv.output, backbone.output])
    image = tf.convert_to_tensor(prepared.model_input[None, ...], dtype=tf.float32)
    with tf.GradientTape() as tape:
        conv_outputs, backbone_output = feature_model(image, training=False)
        x = model.get_layer("global_average_pooling2d")(backbone_output)
        x = model.get_layer("dropout")(x, training=False)
        scores = model.get_layer("dense")(x)
        chosen = int(tf.argmax(scores[0]).numpy()) if class_index is None else int(class_index)
        if not 0 <= chosen < 5:
            raise ValueError("class_index must be between 0 and 4")
        score = scores[:, chosen]
    gradients = tape.gradient(score, conv_outputs)
    if gradients is None:
        raise RuntimeError("Could not calculate Grad-CAM gradients for conv5_block3_out.")
    weights = tf.reduce_mean(gradients, axis=(0, 1, 2))
    heatmap = tf.reduce_sum(conv_outputs[0] * weights[None, None, :], axis=-1)
    heatmap = tf.maximum(heatmap, 0)
    maximum = tf.reduce_max(heatmap)
    heatmap = tf.where(maximum > 0, heatmap / maximum, tf.zeros_like(heatmap)).numpy()
    height, width = prepared.display_rgb.shape[:2]
    heatmap = cv2.resize(heatmap, (width, height), interpolation=cv2.INTER_LINEAR)
    colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    colored = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
    overlay = cv2.addWeighted(prepared.display_rgb, 0.60, colored, 0.40, 0)
    return scores[0].numpy(), heatmap, colored, overlay


def generate_gradcam(model: tf.keras.Model, prepared: PreparedImage,
                     class_index: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Return a normalized grayscale heatmap and RGB overlay at preview size."""
    _, heatmap, _, overlay = _run_gradcam(model, prepared, class_index)
    return heatmap, overlay


def predict_and_generate_gradcam(
    model: tf.keras.Model, prepared: PreparedImage
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return softmax scores, a Jet-colored RGB heatmap, and overlay in one pass."""
    probabilities, _, colored, overlay = _run_gradcam(model, prepared)
    return probabilities, colored, overlay
