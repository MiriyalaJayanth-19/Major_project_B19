"""Image-quality heuristics adapted from the final checker notebook cell."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError

from .config import SUPPORTED_FORMATS

MIN_WIDTH = 256
MIN_HEIGHT = 256
MIN_MEAN_BRIGHTNESS = 20.0
MAX_MEAN_BRIGHTNESS = 245.0
MIN_NON_DARK_RATIO = 0.10
MIN_BLUR_SCORE = 15.0


def check_image_quality(image_path: str | Path) -> dict:
    """Return PASS/FAIL and notebook-style heuristic metrics and reasons."""
    path = Path(image_path)
    result = {"image": path.name, "status": "FAIL", "reasons": [], "width": None,
              "height": None, "blur_score": None, "mean_brightness": None,
              "contrast_std": None, "non_dark_ratio": None,
              "retinal_field_ratio": None}
    if not path.is_file():
        result["reasons"].append("File not found")
        return result
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        result["reasons"].append("Unsupported file extension")
        return result
    try:
        with Image.open(path) as image:
            image.verify()
        raw = np.fromfile(str(path), dtype=np.uint8)
        bgr = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    except (UnidentifiedImageError, OSError, ValueError):
        result["reasons"].append("Invalid or unreadable image")
        return result
    if bgr is None:
        result["reasons"].append("Invalid or unreadable image")
        return result

    height, width = bgr.shape[:2]
    result.update(width=width, height=height)
    reasons = result["reasons"]
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        reasons.append("Resolution too low")
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    standard = cv2.resize(gray, (512, 512), interpolation=cv2.INTER_AREA)
    mask = standard > 15
    blur = 0.0
    if int(mask.sum()) >= 100:
        blur = float(cv2.Laplacian(standard, cv2.CV_64F)[mask].var())
    brightness = float(gray.mean())
    contrast = float(gray.std())
    non_dark = float((gray > 10).mean())
    retinal_field = float((gray > 15).mean())
    result.update(blur_score=round(blur, 2), mean_brightness=round(brightness, 2),
                  contrast_std=round(contrast, 2), non_dark_ratio=round(non_dark, 4),
                  retinal_field_ratio=round(retinal_field, 4))
    if blur < MIN_BLUR_SCORE:
        reasons.append("Possible blur or poor image detail")
    if brightness < MIN_MEAN_BRIGHTNESS:
        reasons.append("Image too dark")
    elif brightness > MAX_MEAN_BRIGHTNESS:
        reasons.append("Image too bright")
    if non_dark < MIN_NON_DARK_RATIO:
        reasons.append("Insufficient visible image area")
    if contrast < 8.0:
        reasons.append("Very low contrast")
    center = gray[int(height * 0.1):int(height * 0.9), int(width * 0.1):int(width * 0.9)]
    if center.size == 0 or float(center.mean()) < 10:
        reasons.append("No clearly visible central retinal field")
    result["status"] = "PASS" if not reasons else "FAIL"
    if not reasons:
        reasons.append("No heuristic issues detected")
    return result
