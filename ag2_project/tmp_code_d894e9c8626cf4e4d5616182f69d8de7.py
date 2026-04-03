#!/usr/bin/env python3
import os
import json
PROJECT_FOLDER = os.environ.get('PROJECT_FOLDER', 'ag2_project')
os.makedirs(PROJECT_FOLDER, exist_ok=True)
os.chdir(PROJECT_FOLDER)

PATHS = {
    'data_raw': os.path.join(PROJECT_FOLDER, 'data', 'raw'),
    'data_processed': os.path.join(PROJECT_FOLDER, 'data', 'processed'),
    'plots_v1': os.path.join(PROJECT_FOLDER, 'plots', 'v1'),
    'plots_v2': os.path.join(PROJECT_FOLDER, 'plots', 'v2'),
    'plots_manifests': os.path.join(PROJECT_FOLDER, 'plots', 'manifests'),
    'reports_latex': os.path.join(PROJECT_FOLDER, 'reports', 'latex'),
    'reports_pdf': os.path.join(PROJECT_FOLDER, 'reports', 'pdf'),
    'scripts': os.path.join(PROJECT_FOLDER, 'scripts', 'generated'),
    'tmp': os.path.join(PROJECT_FOLDER, 'tmp'),
}
for _path in PATHS.values():
    os.makedirs(_path, exist_ok=True)

PLOTS_DIR_V1 = PATHS['plots_v1']
PLOTS_DIR_V2 = PATHS['plots_v2']

PLOT_SELECTED_JSON = os.environ.get('PLOT_SELECTED_JSON', '[]')
try:
    plot_selected = json.loads(PLOT_SELECTED_JSON)
except Exception:
    plot_selected = []

PLOTS_TO_REGENERATE_JSON = os.environ.get('PLOTS_TO_REGENERATE_JSON', '[]')
try:
    plots_to_regenerate = json.loads(PLOTS_TO_REGENERATE_JSON)
except Exception:
    plots_to_regenerate = []

def _ensure_materials_data_json():
    materials_path = os.path.join(PATHS['data_processed'], 'materials_data.json')
    final_conclusion_path = os.path.join(PATHS['data_processed'], 'final_conclusion.json')
    if os.path.exists(materials_path):
        return
    if not os.path.exists(final_conclusion_path):
        return
    try:
        with open(final_conclusion_path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    except Exception:
        return
    mp_results = payload.get('mp_results')
    analysis_summary = payload.get('analysis_summary')
    final_conclusion = payload.get('final_conclusion')
    if mp_results is None:
        return
    with open(materials_path, 'w', encoding='utf-8') as f:
        json.dump(
            {
                'mp_results': mp_results,
                'analysis_summary': analysis_summary,
                'final_conclusion': final_conclusion,
            },
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

_ensure_materials_data_json()

import os
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load materials data
data_path = os.path.join(PATHS["data_processed"], "materials_data.json")
with open(data_path, "r") as f:
    payload = json.load(f)
mp_results = payload.get("mp_results", [])

# Paths for outputs
data_processed_path = PATHS["data_processed"]
plots_v1_path = PATHS["plots_v1"]
plots_v2_path = PATHS["plots_v2"]
plots_manifests_path = PATHS["plots_manifests"]

# Runtime check for plots_to_regenerate
is_v2 = isinstance(plots_to_regenerate, list) and len(plots_to_regenerate) > 0

# CSV and summary table
summary_table = []
for material in mp_results:
    material_id = material.get("material_id")
    formula_pretty = material.get("formula_pretty")
    band_gap = material.get("band_gap")
    energy_above_hull = material.get("energy_above_hull", material.get("e_above_hull"))
    density = material.get("density")
    summary_table.append({
        "material_id": material_id,
        "formula_pretty": formula_pretty,
        "band_gap": band_gap,
        "energy_above_hull": energy_above_hull,
        "density": density
    })

# Save summary table as CSV
summary_df = pd.DataFrame(summary_table)
summary_csv_path = os.path.join(data_processed_path, "summary_table.csv")
summary_df.to_csv(summary_csv_path, index=False)

# Print summary table
print(summary_df.to_string(index=False))

# Plot generation
manifest = []
for plot_spec in plot_selected:
    plot_id = plot_spec["plot_id"]
    title = plot_spec["title"]
    description = plot_spec["description"]
    plot_type = plot_spec["plot_type"]
    axes = plot_spec["axes"]

    if is_v2 and plot_id not in plots_to_regenerate:
        continue

    # Determine output path
    slug = title.lower().replace(" ", "_")
    if is_v2:
        out_path = os.path.join(plots_v2_path, f"{plot_id}_{slug}.png")
    else:
        out_path = os.path.join(plots_v1_path, f"{plot_id}_{slug}.png")

    # Scatter 2D plot
    if plot_type == "scatter_2d":
        x_data = [m.get(axes["x"]) for m in mp_results if axes["x"] in m]
        y_data = [m.get(axes["y"]) for m in mp_results if axes["y"] in m]
        if x_data and y_data:
            plt.figure()
            plt.scatter(x_data, y_data)
            plt.xlabel("Band Gap (eV)" if axes["x"] == "band_gap" else "Energy Above Hull (eV/atom)")
            plt.ylabel("Density (g/cm³)" if axes["y"] == "density" else
                       "Band Gap (eV)")
            plt.title(title)
            plt.savefig(out_path)
            assert os.path.exists(out_path)
            plt.close()
        else:
            plt.figure()
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
            plt.savefig(out_path)
            assert os.path.exists(out_path)
            plt.close()
    # Histogram plot
    elif plot_type == "histogram":
        hist_data = [m.get(axes["x"]) for m in mp_results if axes["x"] in m]
        if hist_data:
            plt.figure()
            plt.hist(hist_data, bins=30, edgecolor='black')
            plt.xlabel("Band Gap (eV)" if axes["x"] == "band_gap" else "Energy Above Hull (eV/atom)")
            plt.title(title)
            plt.savefig(out_path)
            assert os.path.exists(out_path)
            plt.close()
        else:
            plt.figure()
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
            plt.savefig(out_path)
            assert os.path.exists(out_path)
            plt.close()

    manifest.append({
        "plot_id": plot_id,
        "name": f"{plot_id}_{slug}.png",
        "path": out_path,
        "description": description
    })

manifest_name = "plots_v2_manifest.json" if is_v2 else "plots_v1_manifest.json"
manifest_path = os.path.join(plots_manifests_path, manifest_name)
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=4)
