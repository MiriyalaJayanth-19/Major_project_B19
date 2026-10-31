"""Model construction and inference for the saved ResNet50 weights."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import tensorflow as tf

from .config import (CLASS_LABELS, MODEL_INPUT_SIZE, MODEL_PATH, NUM_CLASSES,
                     REFERABLE_GRADES, REFERABLE_THRESHOLD)
from .preprocessing import PreparedImage, preprocess_fundus


def build_resnet50_model() -> tf.keras.Model:
    """Rebuild the architecture recorded in the training notebook/config."""
    inputs = tf.keras.Input(shape=(*MODEL_INPUT_SIZE, 3), name="input_layer_1")
    backbone = tf.keras.applications.ResNet50(
        weights=None, include_top=False, input_shape=(*MODEL_INPUT_SIZE, 3), name="resnet50"
    )
    backbone.trainable = False
    x = backbone(inputs, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D(name="global_average_pooling2d")(x)
    x = tf.keras.layers.Dropout(0.3, name="dropout")(x)
    outputs = tf.keras.layers.Dense(NUM_CLASSES, activation="softmax", name="dense")(x)
    return tf.keras.Model(inputs, outputs, name="functional")


def load_model(checkpoint: str | Path = MODEL_PATH) -> tf.keras.Model:
    """Load actual local weights, with a clear failure if missing/incompatible."""
    checkpoint = Path(checkpoint)
    if not checkpoint.is_file():
        raise FileNotFoundError(
            f"ResNet50 weights were not found at {checkpoint}. Place the project checkpoint there."
        )
    model = build_resnet50_model()
    try:
        model.load_weights(str(checkpoint))
    except Exception as exc:
        raise RuntimeError(f"Could not load ResNet50 weights from {checkpoint}: {exc}") from exc
    return model


def predict_prepared(model: tf.keras.Model, prepared: PreparedImage,
                     threshold: float = REFERABLE_THRESHOLD) -> dict:
    """Predict grades and derive binary referral from summed class probabilities."""
    probabilities = np.asarray(model(prepared.model_input[None, ...], training=False))[0]
    return prediction_from_probabilities(probabilities, threshold)


def prediction_from_probabilities(probabilities: np.ndarray,
                                  threshold: float = REFERABLE_THRESHOLD) -> dict:
    """Validate and format five-class softmax scores for the interface."""
    probabilities = np.asarray(probabilities, dtype=np.float32).reshape(-1)
    if probabilities.shape != (NUM_CLASSES,) or not np.isfinite(probabilities).all():
        raise ValueError(f"Expected {NUM_CLASSES} finite class probabilities; got {probabilities.shape}.")
    if np.any(probabilities < 0) or np.any(probabilities > 1) or not np.isclose(probabilities.sum(), 1, atol=1e-3):
        raise ValueError("Model output is not a valid five-class softmax probability vector.")
    grade = int(np.argmax(probabilities))
    referable_probability = float(probabilities[list(REFERABLE_GRADES)].sum())
    return {
        "grade": grade,
        "grade_label": CLASS_LABELS[grade],
        "probabilities": probabilities.astype(float),
        "referable_probability": referable_probability,
        "binary_label": "Referable DR" if referable_probability >= threshold else "Non-referable DR",
        "binary_threshold": threshold,
    }


def predict_image(model: tf.keras.Model, image_path: str | Path,
                  threshold: float = REFERABLE_THRESHOLD) -> tuple[PreparedImage, dict]:
    prepared = preprocess_fundus(image_path)
    return prepared, predict_prepared(model, prepared, threshold)
