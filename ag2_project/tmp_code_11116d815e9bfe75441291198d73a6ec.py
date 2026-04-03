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
import matplotlib.pyplot as plt
import os

# Load materials data
with open('materials_data.json') as f:
    payload = json.load(f)
    mp_results = payload.get('mp_results', [])

# Extract data for CSV and plots
csv_summary = []

for material in mp_results:
    material_id = material.get("material_id", "")
    formula_pretty = material.get("formula_pretty", "")
    band_gap = material.get("band_gap", "")
    energy_above_hull = material.get("energy_above_hull", material.get("e_above_hull", ""))
    density = material.get("density", "")

    # Append data to CSV
    csv_summary.append([material_id, formula_pretty, band_gap, energy_above_hull, density])

# Export CSV
import csv
with open('summary_table.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density'])
    csvwriter.writerows(csv_summary)

# Print readable table to stdout
from tabulate import tabulate
print(tabulate(csv_summary, headers=['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density'], tablefmt='pretty'))

# Selected plots specifications
plot_selected = [
    {
        "plot_id": "plot_1",
        "title": "Band Gap vs Density",
        "description": "Scatter plot of band gap vs density for selected stable materials.",
        "data_requirements": ["band_gap", "density"],
        "axes": {"type": "2d", "x": "band_gap", "y": "density", "z": null, "intensity": null},
        "rationale": "Visualizing the correlation between electronic and physical properties.",
        "plot_type": "scatter_2d"
    },
    {
        "plot_id": "plot_6",
        "title": "Density vs Band Gap Intensity Heatmap",
        "description": "Heatmap showing intensity of material occurrence at different density and band gap values.",
        "data_requirements": ["band_gap", "density"],
        "axes": {"type": "heatmap", "x": "band_gap", "y": "density", "z": null, "intensity": "count"},
        "rationale": "Captures frequency of occurrences of combinations indicative of ideal qualities.",
        "plot_type": "heatmap_2d"
    },
    {
        "plot_id": "plot_8",
        "title": "3D Scatter of Band Gap, Density, and Stability",
        "description": "3D scatter plot depicting relationship among band gap, density, and energy above hull.",
        "data_requirements": ["band_gap", "density", "energy_above_hull"],
        "axes": {"type": "3d", "x": "band_gap", "y": "density", "z": "energy_above_hull", "intensity": null},
        "rationale": "Provides a comprehensive view for material selection.",
        "plot_type": "scatter_3d"
    },
    {
        "plot_id": "plot_4",
        "title": "Materials Stability Distribution",
        "description": "Bar plot showing materials' stability based on energy above hull values.",
        "data_requirements": ["energy_above_hull"],
        "axes": {"type": "categorical", "x": "energy_above_hull", "y": "count", "z": null, "intensity": null},
        "rationale": "Provides quick insight into stability for durable applications.",
        "plot_type": "bar"
    },
    {
        "plot_id": "plot_7",
        "title": "Energy Above Hull vs Band Gap",
        "description": "Scatter plot of energy above hull vs band gap for retrieved materials.",
        "data_requirements": ["energy_above_hull", "band_gap"],
        "axes": {"type": "2d", "x": "energy_above_hull", "y": "band_gap", "z": null, "intensity": null},
        "rationale": "Explores stability and electronic properties.",
        "plot_type": "scatter_2d"
    }
]

# Create plots
for plot in plot_selected:
    plot_id = plot['plot_id']
    title = plot['title']
    description = plot['description']
    plot_type = plot['plot_type']
    axes = plot['axes']

    slug = title.lower().replace(' ', '_')

    # Extract respective data
    if plot_type == 'scatter_2d':
        x_data = [m.get(axes['x'], None) for m in mp_results if m.get(axes['x'], None) is not None]
        y_data = [m.get(axes['y'], None) for m in mp_results if m.get(axes['y'], None) is not None]

        if x_data and y_data:
            plt.figure(figsize=(10, 6))
            plt.scatter(x_data, y_data, alpha=0.7)
            plt.xlabel(axes['x'])
            plt.ylabel(axes['y'])
            plt.title(title)
            out_path = os.path.join("plots", f"{plot_id}_{slug}.png")
            plt.savefig(out_path)
            if not os.path.exists(out_path):
                raise RuntimeError(f"Failed to save plot {out_path}")
            plt.close()

    elif plot_type == 'heatmap_2d':
        x_data = [m.get(axes['x'], None) for m in mp_results if m.get(axes['x'], None) is not None]
        y_data = [m.get(axes['y'], None) for m in mp_results if m.get(axes['y'], None) is not None]
        if x_data and y_data:
            plt.figure(figsize=(10, 6))
            plt.hexbin(x_data, y_data, gridsize=50, cmap='Blues', mincnt=1)
            plt.colorbar(label='Counts')
            plt.xlabel(axes['x'])
            plt.ylabel(axes['y'])
            plt.title(title)
            out_path = os.path.join("plots", f"{plot_id}_{slug}.png")
            plt.savefig(out_path)
            if not os.path.exists(out_path):
                raise RuntimeError(f"Failed to save plot {out_path}")
            plt.close()

    elif plot_type == 'scatter_3d':
from mpl_toolkits.mplot3d import Axes3D  # Import necessary for 3D plotting
        x_data = [m.get(axes['x'], None) for m in mp_results if m.get(axes['x'], None) is not None]
        y_data = [m.get(axes['y'], None) for m in mp_results if m.get(axes['y'], None) is not None]
        z_data = [m.get(axes['z'], None) for m in mp_results if m.get(axes['z'], None) is not None]
        if x_data and y_data and z_data:
            fig = plt.figure(figsize=(10, 7))
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(x_data, y_data, z_data, alpha=0.7)
            ax.set_xlabel(axes['x'])
            ax.set_ylabel(axes['y'])
            ax.set_zlabel(axes['z'])
            plt.title(title)
            out_path = os.path.join("plots", f"{plot_id}_{slug}.png")
            plt.savefig(out_path)
            if not os.path.exists(out_path):
                raise RuntimeError(f"Failed to save plot {out_path}")
            plt.close()

    elif plot_type == 'bar':
        eah_data = [m.get('energy_above_hull', None) for m in mp_results]
        stability_categories = {"stable_eah_eq_0": "Stable (E=0)", "near_stable_le_0p05": "Near Stable (E≤0.05)"}
        eah_count = {"Stable (E=0)": 0, "Near Stable (E≤0.05)": 0}
        for eah in eah_data:
            if eah is not None and eah <= 0.05:
                eah_count[stability_categories["near_stable_le_0p05"]] += 1
            elif eah == 0:
                eah_count[stability_categories["stable_eah_eq_0"]] += 1
        categories = list(eah_count.keys())
        values = list(eah_count.values())
        plt.figure(figsize=(8, 5))
        plt.bar(categories, values, color='skyblue')
        plt.xlabel("Stability")
        plt.ylabel("Number of Materials")
        plt.title(title)
        out_path = os.path.join("plots", f"{plot_id}_{slug}.png")
        plt.savefig(out_path)
        if not os.path.exists(out_path):
            raise RuntimeError(f"Failed to save plot {out_path}")
        plt.close()

# Create the manifest
manifest = {
    "plots_v1": []
}
for plot in plot_selected:
    plot_id = plot['plot_id']
    title = plot['title']
    slug = title.lower().replace(' ', '_')
    filename = f"{plot_id}_{slug}.png"
    path = os.path.join("plots", filename)
    manifest["plots_v1"].append({
        "plot_id": plot_id,
        "name": filename,
        "path": path,
        "description": plot['description']
    })

# Write the manifest to a file
manifest_path = 'plots_v1_manifest.json'
manifest_temp = 'plots_v1_manifest.json.tmp'
with open(manifest_temp, 'w') as f:
    json.dump(manifest, f, indent=2)
os.replace(manifest_temp, manifest_path)
