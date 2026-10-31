"""Fundus preprocessing based on the project's preprocessing notebook."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf

from .config import FUNDUS_SIZE, JPEG_QUALITY, MODEL_INPUT_SIZE, RGB_MEAN, RGB_STD


@dataclass(frozen=True)
class PreparedImage:
    """Image views used by the interface and model."""

    display_rgb: np.ndarray
    model_input: np.ndarray


def _read_rgb(image: str | Path | np.ndarray) -> np.ndarray:
    if isinstance(image, np.ndarray):
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError("Expected an RGB image with three channels.")
        return np.ascontiguousarray(image, dtype=np.uint8)
    encoded = np.fromfile(str(image), dtype=np.uint8)
    decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if decoded is None:
        raise ValueError(f"Unable to read image: {image}")
    return cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB)


def resize_with_padding(image: np.ndarray, target_size: int = FUNDUS_SIZE) -> np.ndarray:
    """Resize to a square while preserving aspect ratio and black padding."""
    height, width = image.shape[:2]
    scale = target_size / max(height, width)
    new_width = max(1, round(width * scale))
    new_height = max(1, round(height * scale))
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((target_size, target_size, 3), dtype=image.dtype)
    top = (target_size - new_height) // 2
    left = (target_size - new_width) // 2
    canvas[top:top + new_height, left:left + new_width] = resized
    return canvas


def preprocess_fundus(image: str | Path | np.ndarray) -> PreparedImage:
    """Apply Notebook 2 processing and the ResNet50 training input transform.

    This reproduces CLAHE (LAB L channel), Gaussian blur, >40 dark-border
    cropping, aspect-preserving 512 padding, and the notebook's RGB
    normalization/JPEG export round trip. It then performs the 224 resize and
    ResNet50 ``preprocess_input`` used in the ResNet training notebook.
    """
    rgb = _read_rgb(image)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    lightness, a_channel, b_channel = cv2.split(lab)
    enhanced_l = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8)).apply(lightness)
    enhanced = cv2.cvtColor(cv2.merge((enhanced_l, a_channel, b_channel)), cv2.COLOR_LAB2RGB)
    filtered = cv2.GaussianBlur(enhanced, (5, 5), sigmaX=0)
    gray = cv2.cvtColor(filtered, cv2.COLOR_RGB2GRAY)
    rows, cols = np.where(gray > 40)[0], np.where(gray > 40)[1]
    if rows.size == 0 or cols.size == 0:
        raise ValueError("No fundus foreground was detected after dark-border cropping.")
    cropped = filtered[rows.min():rows.max() + 1, cols.min():cols.max() + 1]
    square = resize_with_padding(cropped)

    mean = np.asarray(RGB_MEAN, dtype=np.float32)
    std = np.asarray(RGB_STD, dtype=np.float32)
    normalized = (square.astype(np.float32) - mean) / std
    uint8_rgb = np.clip(normalized * std + mean, 0, 255).astype(np.uint8)
    ok, encoded = cv2.imencode(
        ".jpg", cv2.cvtColor(uint8_rgb, cv2.COLOR_RGB2BGR),
        [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY],
    )
    if not ok:
        raise ValueError("Could not reproduce the training JPEG preprocessing step.")
    decoded_bgr = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    training_rgb = cv2.cvtColor(decoded_bgr, cv2.COLOR_BGR2RGB)
    resized = tf.image.resize(training_rgb, MODEL_INPUT_SIZE).numpy().astype(np.float32)
    model_input = tf.keras.applications.resnet50.preprocess_input(resized)
    return PreparedImage(display_rgb=uint8_rgb, model_input=model_input)
