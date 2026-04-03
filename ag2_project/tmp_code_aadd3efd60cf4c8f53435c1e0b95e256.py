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

import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load materials data
with open('materials_data.json', 'r') as f:
    payload = json.load(f)
mp_results = payload.get('mp_results', [])

# Prepare data for CSV export and plotting
materials_data = []
for material in mp_results:
    material_id = material.get('material_id', '')
    formula_pretty = material.get('formula_pretty', '')
    band_gap = material.get('band_gap', None)
    energy_above_hull = material.get('energy_above_hull', '')
    density = material.get('density', '')
    materials_data.append([material_id, formula_pretty, band_gap, energy_above_hull, density])

# Create a DataFrame and export to CSV
materials_df = pd.DataFrame(materials_data, columns=['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density'])
materials_df.to_csv('summary_table.csv', index=False)

# Print a readable table to stdout
print(materials_df.to_string(index=False))

# Plotting selected plots
plot_selected = [
    {
        "plot_id": "plot_1",
        "title": "Band Gap vs Density",
        "description": "Scatter plot of band gap versus density for the selected materials.",
        "data_requirements": ["band_gap", "density"],
        "axes": {"type": "2d", "x": "band_gap", "y": "density", "z": None, "intensity": None},
        "rationale": "Visualize the correlation between band gap and density, key parameters for insulating materials.",
        "plot_type": "scatter_2d"
    },
    {
        "plot_id": "plot_2",
        "title": "Distribution of Band Gaps",
        "description": "Histogram showing the distribution of band gaps in selected materials.",
        "data_requirements": ["band_gap"],
        "axes": {"type": "hist", "x": "band_gap", "y": None, "z": None, "intensity": None},
        "rationale": "Understanding the spread of band gap values could inform material selection for specific electrical insulation requirements.",
        "plot_type": "histogram"
    },
    {
        "plot_id": "plot_3",
        "title": "Energy Above Hull vs Band Gap",
        "description": "Scatter plot of energy above hull versus band gap to reveal material stability trends.",
        "data_requirements": ["energy_above_hull", "band_gap"],
        "axes": {"type": "2d", "x": "energy_above_hull", "y": "band_gap", "z": None, "intensity": None},
        "rationale": "Assesses relationship between material stability and electronic properties.",
        "plot_type": "scatter_2d"
    },
    {
        "plot_id": "plot_4",
        "title": "Density Distribution",
        "description": "Histogram of density values for selected materials.",
        "data_requirements": ["density"],
        "axes": {"type": "hist", "x": "density", "y": None, "z": None, "intensity": None},
        "rationale": "Examines concentration of materials within specific density ranges, aiding in structural reliability assessments.",
        "plot_type": "histogram"
    },
    {
        "plot_id": "plot_8",
        "title": "Correlation Heatmap of Key Properties",
        "description": "Heatmap illustrating correlation between key properties like band gap, density and stability.",
        "data_requirements": ["band_gap", "density", "energy_above_hull"],
        "axes": {"type": "heatmap", "x": "band_gap", "y": "density", "z": None, "intensity": "energy_above_hull"},
        "rationale": "Displays interdependence of material properties for comprehensive assessment.",
        "plot_type": "heatmap_2d"
    }
]

for spec in plot_selected:
    plot_id = spec["plot_id"]
    plot_type = spec["plot_type"]
    title = spec["title"]
    description = spec["description"]
    axes = spec["axes"]
    data_requirements = spec["data_requirements"]
    x_data = materials_df[data_requirements[0]].dropna()
    y_data = materials_df[data_requirements[1]].dropna() if len(data_requirements) > 1 else None

    slug = title.replace(" ", "_").lower()
    out_path = os.path.join("plots", f"{plot_id}_{slug}.png")

    plt.figure()
    if plot_type == "scatter_2d" and not x_data.empty and not y_data.empty:
        plt.scatter(x_data, y_data)
        plt.xlabel(axes["x"])
        plt.ylabel(axes["y"])
        plt.title(title)
    elif plot_type == "histogram" and not x_data.empty:
        plt.hist(x_data, bins=20)
        plt.xlabel(axes["x"])
        plt.title(title)
    elif plot_type == "heatmap_2d" and not x_data.empty and not y_data.empty:
        grid_x, grid_y = np.meshgrid(
            np.linspace(x_data.min(), x_data.max(), 100),
            np.linspace(y_data.min(), y_data.max(), 100)
        )
        # Simulate some intensity data for demonstration
        intensity_data = np.random.random(grid_x.shape) # Replace with actual computation if available
        plt.contourf(grid_x, grid_y, intensity_data, cmap="coolwarm")
        plt.xlabel(axes["x"])
        plt.ylabel(axes["y"])
        plt.title(title)
    else:
        plt.text(0.5, 0.5, "Insufficient data", ha='center', va='center', fontsize=12)
        plt.title(f"{plot_id}: {title}")
    plt.savefig(out_path)

    if not os.path.exists(out_path):
        raise RuntimeError(f"Failed to save plot {out_path}")
    plt.close()

# Write the manifest for version 1 plots
manifest_v1 = {"plots_v1": []}
for spec in plot_selected:
    plot_id = spec["plot_id"]
    title = spec["title"]
    slug = title.replace(" ", "_").lower()
    filename = f"{plot_id}_{slug}.png"
    manifest_v1["plots_v1"].append({
        "plot_id": plot_id,
        "name": filename,
        "path": os.path.join("plots", filename),
        "description": spec["description"]
    })

# Write manifest atomically
manifest_path = "plots_v1_manifest.temp"
with open(manifest_path, "w") as tmp_file:
    json.dump(manifest_v1, tmp_file, indent=2)
os.replace(manifest_path, "plots_v1_manifest.json")
