import numpy as np

from src.preprocessing import preprocess_fundus


def test_preprocessing_shape_type_and_rgb_display():
    image = np.zeros((300, 420, 3), dtype=np.uint8)
    image[30:270, 50:370] = (150, 90, 55)
    image[100:200, 120:180] = (210, 140, 100)
    prepared = preprocess_fundus(image)
    assert prepared.display_rgb.shape == (512, 512, 3)
    assert prepared.display_rgb.dtype == np.uint8
    assert prepared.model_input.shape == (224, 224, 3)
    assert prepared.model_input.dtype == np.float32
    assert np.isfinite(prepared.model_input).all()
    assert not np.array_equal(prepared.display_rgb[..., 0], prepared.display_rgb[..., 2])
