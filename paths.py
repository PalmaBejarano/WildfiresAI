import os

BASE_DIR = os.path.abspath("ag2_project")

PATHS = {
    "data_raw": os.path.join(BASE_DIR, "data", "raw"),
    "data_processed": os.path.join(BASE_DIR, "data", "processed"),
    "plots_v1": os.path.join(BASE_DIR, "plots", "v1"),
    "plots_v2": os.path.join(BASE_DIR, "plots", "v2"),
    "plots_manifests": os.path.join(BASE_DIR, "plots", "manifests"),
    "reports_latex": os.path.join(BASE_DIR, "reports", "latex"),
    "reports_pdf": os.path.join(BASE_DIR, "reports", "pdf"),
    "scripts": os.path.join(BASE_DIR, "scripts", "generated"),
    "tmp": os.path.join(BASE_DIR, "tmp"),
}

for path in PATHS.values():
    os.makedirs(path, exist_ok=True)
    