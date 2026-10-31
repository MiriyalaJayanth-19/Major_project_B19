"""Print the setup and Grad-CAM code cells from the project notebook."""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "Notebooks" / "gradcam-resnet.ipynb"

with NOTEBOOK_PATH.open("r", encoding="utf-8") as notebook_file:
    notebook = json.load(notebook_file)

code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
for index, cell in enumerate(code_cells[:8]):
    print(f"=== CELL {index} ===")
    print("".join(cell["source"]))
    print()
