#!/usr/bin/env python3
import os
import json
PROJECT_FOLDER = os.environ.get('PROJECT_FOLDER', 'ag2_project')
os.makedirs(PROJECT_FOLDER, exist_ok=True)
os.chdir(PROJECT_FOLDER)

PLOTS_DIR_V1 = os.path.join(PROJECT_FOLDER, 'plots')
PLOTS_DIR_V2 = os.path.join(PROJECT_FOLDER, 'plots_v2')
os.makedirs(PLOTS_DIR_V1, exist_ok=True)
os.makedirs(PLOTS_DIR_V2, exist_ok=True)

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
    if os.path.exists('materials_data.json'):
        return
    if not os.path.exists('final_conclusion.json'):
        return
    try:
        with open('final_conclusion.json', 'r', encoding='utf-8') as f:
            payload = json.load(f)
    except Exception:
        return
    mp_results = payload.get('mp_results')
    analysis_summary = payload.get('analysis_summary')
    final_conclusion = payload.get('final_conclusion')
    if mp_results is None:
        return
    with open('materials_data.json', 'w', encoding='utf-8') as f:
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
import pandas as pd

# Load data
with open('materials_data.json') as f:
    payload = json.load(f)
    mp_results = payload.get("mp_results", [])

# Prepare data frame for table
materials_data = []
for material in mp_results:
    material_id = material.get("material_id", "")
    formula_pretty = material.get("formula_pretty", "")
    band_gap = material.get("band_gap", "")
    energy_above_hull = material.get("e_above_hull", material.get("energy_above_hull", ""))
    density = material.get("density", "")
    elements = material.get("elements", [])

    # Filter conditions
    if energy_above_hull is not None and 0.0 <= energy_above_hull <= 0.05 \
       and band_gap is not None and 3.0 <= band_gap <= 20.0 \
       and density is not None and 3.0 <= density <= 10.0 \
       and not any(ele in elements for ele in ["Pb", "Cd", "Hg"]):
        materials_data.append({
            "material_id": material_id,
            "formula_pretty": formula_pretty,
            "band_gap": band_gap,
            "energy_above_hull": energy_above_hull,
            "density": density
        })

# Export to CSV
if materials_data:
    df = pd.DataFrame(materials_data)
    df.to_csv('summary_table.csv', index=False)

# Print table
print(f"{'material_id':<15} {'formula_pretty':<20} {'band_gap':<10} {'energy_above_hull':<20} {'density':<10}")
for row in materials_data:
    print(f"{row['material_id']:<15} {row['formula_pretty']:<20} {row['band_gap']:<10} {row['energy_above_hull']:<20} {row['density']:<10}")

# Plot configurations
plot_selected = [
    {
        "plot_id": "plot_1",
        "title": "Band Gap Distribution of Inorganic Materials",
        "axes": {"type": "hist", "x": "band_gap"},
        "plot_type": "histogram"
    },
    {
        "plot_id": "plot_2",
        "title": "Density Distribution of Inorganic Materials",
        "axes": {"type": "hist", "x": "density"},
        "plot_type": "histogram"
    },
    {
        "plot_id": "plot_3",
        "title": "Energy Above Hull Analysis",
        "axes": {"type": "hist", "x": "energy_above_hull"},
        "plot_type": "histogram"
    },
    {
        "plot_id": "plot_4",
        "title": "Correlation Between Band Gap and Density",
        "axes": {"type": "2d", "x": "band_gap", "y": "density"},
        "plot_type": "scatter_2d"
    },
    {
        "plot_id": "plot_5",
        "title": "Stability versus Band Gap",
        "axes": {"type": "2d", "x": "energy_above_hull", "y": "band_gap"},
        "plot_type": "scatter_2d"
    }
]

for plot_spec in plot_selected:
    plot_id = plot_spec["plot_id"]
    title = plot_spec["title"]
    plot_type = plot_spec["plot_type"]

    if plot_type == "histogram":
        x_data_key = plot_spec["axes"]["x"]
        x_data = [material.get(x_data_key) for material in materials_data if material.get(x_data_key) is not None]
        plt.figure()
        plt.hist(x_data, bins=20, color='blue', alpha=0.7)
        plt.title(title)
        plt.xlabel(x_data_key)
        plt.ylabel('Frequency')
    elif plot_type == "scatter_2d":
        x_data_key = plot_spec["axes"]["x"]
        y_data_key = plot_spec["axes"]["y"]
        x_data = [material.get(x_data_key) for material in materials_data if material.get(x_data_key) is not None]
        y_data = [material.get(y_data_key) for material in materials_data if material.get(y_data_key) is not None]
        plt.figure()
        plt.scatter(x_data, y_data, color='red', alpha=0.5)
        plt.title(title)
        plt.xlabel(x_data_key)
        plt.ylabel(y_data_key)
    else:
        plt.figure()
        plt.text(0.5, 0.5, 'Insufficient data', fontsize=12, ha='center')
        plt.title(f"Placeholder for {plot_id}")

    slug = title.lower().replace(' ', '_').replace(',', '')
    out_path = os.path.join("plots", f"{plot_id}_{slug}.png")
    plt.savefig(out_path)
    if not os.path.exists(out_path):
        raise RuntimeError(f"Failed to save the plot at {out_path}")
    plt.close()

# Save the plot manifest
manifest = {"plots_v1": []}
for plot_spec in plot_selected:
    plot_id = plot_spec["plot_id"]
    title = plot_spec["title"]
    slug = title.lower().replace(' ', '_').replace(',', '')
    filename = f"{plot_id}_{slug}.png"
    manifest["plots_v1"].append({
        "plot_id": plot_id,
        "name": filename,
        "path": os.path.join("plots", filename),
        "description": plot_spec["description"]
    })

with open('plots_v1_manifest.json', 'w') as manifest_file:
    json.dump(manifest, manifest_file, indent=2)
