import numpy as np
import pytest

from src.config import MODEL_PATH
from src.gradcam import predict_and_generate_gradcam
from src.predictor import load_model
from src.preprocessing import PreparedImage


def test_gradcam_dimensions_with_real_checkpoint():
    if not MODEL_PATH.is_file():
        pytest.skip("Local checkpoint is not present")
    model = load_model()
    display = np.full((512, 512, 3), 100, dtype=np.uint8)
    prepared = PreparedImage(display, np.zeros((224, 224, 3), dtype=np.float32))
    scores, heatmap, overlay = predict_and_generate_gradcam(model, prepared)
    assert scores.shape == (5,)
    assert heatmap.shape == (512, 512, 3)
    assert not np.array_equal(heatmap[..., 0], heatmap[..., 2])
    assert overlay.shape == (512, 512, 3)
    assert overlay.dtype == np.uint8
    assert np.isfinite(heatmap).all()
