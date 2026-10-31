from pathlib import Path

import numpy as np
import pytest

from src.config import CLASS_LABELS, MODEL_PATH
from src.predictor import load_model, predict_prepared
from src.preprocessing import PreparedImage


class FakeModel:
    def __call__(self, batch, training=False):
        return np.asarray([[0.05, 0.10, 0.60, 0.15, 0.10]], dtype=np.float32)


def test_prediction_probabilities_and_binary_derivation():
    prepared = PreparedImage(np.zeros((512, 512, 3), np.uint8), np.zeros((224, 224, 3), np.float32))
    result = predict_prepared(FakeModel(), prepared)
    assert result["grade"] == 2
    assert result["grade_label"] == CLASS_LABELS[2]
    assert len(result["probabilities"]) == 5
    assert np.isclose(sum(result["probabilities"]), 1)
    assert result["binary_label"] == "Referable DR"
    assert np.isclose(result["referable_probability"], 0.85)


def test_load_actual_checkpoint_when_available():
    if not MODEL_PATH.is_file():
        pytest.skip("Local checkpoint is not present")
    model = load_model()
    assert tuple(model.input_shape[1:]) == (224, 224, 3)
    assert model.output_shape[-1] == 5
