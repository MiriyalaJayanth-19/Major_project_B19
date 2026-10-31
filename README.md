# AI_DR screening research prototype

Gradio application for the existing five-class fine-tuned ResNet50. The app uses the project notebooks as its source of truth and does not train or replace the model.

## Findings from the notebooks and local artifacts

- `Notebooks/resnet-training.ipynb` defines a 224×224×3 ResNet50 (`include_top=False`, global average pooling, dropout 0.3, five-unit softmax Dense head). Grades are ordered 0 through 4: No DR, Mild, Moderate, Severe, Proliferative DR.
- Its input pipeline decodes the previously preprocessed JPEG, resizes to 224×224 with `tf.image.resize`, then calls `tf.keras.applications.resnet50.preprocess_input`. The output is a five-class softmax probability vector.
- `Notebooks/pre-processing.ipynb` applies LAB lightness CLAHE (clip 5, tiles 8×8), Gaussian blur (5×5), crop to pixels with grayscale >40, aspect-preserving 512×512 padding, the recorded RGB channel standardization, then de-standardizes and writes JPEG at quality 95. The app reproduces these steps and the JPEG round trip before applying the ResNet input transform.
- `Notebooks/image-quality-checker.ipynb` ends with the standardized 512×512 Laplacian blur check (threshold 15), minimum 256×256 dimensions, brightness 20–245, non-dark fraction ≥0.10, contrast standard deviation ≥8, and central retinal field mean ≥10. These are heuristics, not fundus-authenticity or clinical-suitability validation.
- `Notebooks/gradcam-resnet.ipynb` uses nested backbone `resnet50`, target convolution `conv5_block3_out`, and a 60/40 original/heatmap overlay. The app uses that target with the same already prepared model input.
- Binary screening follows the evaluation convention: grades 0–1 non-referable; grades 2–4 referable. The referable probability is the sum of softmax grades 2–4. A 0.5 threshold is used as the notebook's initial threshold, not claimed to be clinically optimal.
- Local model artifact is `Models/ResNet/resnet50_finetuned_best/model.weights.h5` (about 215 MB). Its metadata reports Keras 3.13.2, and the adjacent config records the five-class ResNet architecture. The app loads these actual weights; it does not fabricate or copy a model file.

## Technical limitation discovered

The notebook's standalone `.keras` checkpoint is not present in this checkout. The local artifact is weights-only, so the app rebuilds the architecture documented by the training notebook and model config and loads `model.weights.h5`. If the weights were exported from a different architecture, loading fails with a clear error. The original `Notebooks/` files are preserved as-is.

## Setup (PowerShell)

Use a supported 64-bit Python version (3.11 or 3.12 is recommended for Windows TensorFlow wheels), then run from the project root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

To start the app from the project root:

```powershell
python app.py
```

Upload a real fundus image as JPG, JPEG, PNG, BMP, TIF, or TIFF. The application reports a quality-check failure and skips prediction when any mandatory heuristic fails. Review the image, predicted grade, probabilities, binary screening estimate, and Grad-CAM visualization together.

## Project layout

```text
AI_DR_Project/
├── app.py
├── src/                 # Model, preprocessing, quality, Grad-CAM, and UI modules
├── assets/              # Optional UI assets
├── tests/               # Unit and checkpoint tests
├── tools/               # Notebook inspection helpers
├── Models/              # Existing trained checkpoints (not committed)
├── Notebooks/           # Original project notebooks, preserved unchanged
├── requirements.txt
└── .env.example
```

The application now runs directly from the project root. The original notebook and model folders remain in place.

## LLM API key

The multilingual explanation area is currently a UI placeholder and does not call an LLM yet. When a provider is selected and the integration is added, put the key in a root-level `.env` file, using `.env.example` as the template:

```dotenv
LLM_API_KEY=replace_with_your_provider_key
```

Do not put the real key in `app.py`, notebooks, or Git. `.env` is ignored by Git. The current placeholder does not read or use this key yet.

## Tests

```powershell
python -m pytest -q
```

Tests requiring TensorFlow need the environment above. `test_prediction.py` attempts loading the actual local checkpoint when present.

## Disclaimer

Academic research prototype only. This system is not clinically validated and must not be used as a diagnosis or to guide treatment. A qualified clinician must interpret retinal images and screening results.
