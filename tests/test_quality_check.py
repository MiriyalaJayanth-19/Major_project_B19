import cv2
import numpy as np

from src.quality_check import check_image_quality


def test_quality_check_rejects_tiny_image(tmp_path):
    path = tmp_path / "tiny.png"
    assert cv2.imwrite(str(path), np.full((100, 100, 3), 100, np.uint8))
    result = check_image_quality(path)
    assert result["status"] == "FAIL"
    assert "Resolution too low" in result["reasons"]


def test_quality_check_rejects_unsupported_format(tmp_path):
    path = tmp_path / "image.gif"
    path.write_bytes(b"not an image")
    result = check_image_quality(path)
    assert result["status"] == "FAIL"
    assert "Unsupported file extension" in result["reasons"]
