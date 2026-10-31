"""Central configuration for the AI_DR application."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PROJECT_ROOT
MODEL_PATH = PROJECT_ROOT / "Models" / "ResNet" / "resnet50_finetuned_best" / "model.weights.h5"
MODEL_INPUT_SIZE = (224, 224)
FUNDUS_SIZE = 512
JPEG_QUALITY = 95
NUM_CLASSES = 5
CLASS_LABELS = (
    "No DR",
    "Mild DR",
    "Moderate DR",
    "Severe DR",
    "Proliferative DR",
)
REFERABLE_GRADES = (2, 3, 4)
REFERABLE_THRESHOLD = 0.5
RGB_MEAN = (133.71985309, 79.52423862, 41.30843877)
RGB_STD = (62.56835813, 38.40553729, 29.33583564)
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
