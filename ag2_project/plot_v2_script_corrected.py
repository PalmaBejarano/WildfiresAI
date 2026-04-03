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
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MaxNLocator

# Load materials data
with open('materials_data.json') as f:
    payload = json.load(f)

mp_results = payload.get('mp_results', [])

# Export CSV summary
csv_headers = ['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density']

summary_table = []
for material in mp_results:
    material_id = material.get('material_id', '')
    formula_pretty = material.get('formula_pretty', '')
    band_gap = material.get('band_gap', '')
    energy_above_hull = material.get('energy_above_hull', material.get('e_above_hull', ''))
    density = material.get('density', '')

    summary_table.append([material_id, formula_pretty, band_gap, energy_above_hull, density])

summary_csv_path = "summary_table.csv"
with open(summary_csv_path, 'w') as f:
    f.write(','.join(csv_headers) + '\n')
    for row in summary_table:
        f.write(','.join(map(str, row)) + '\n')

# Print table to stdout
print(f"{'Material ID':<20} {'Formula':<30} {'Band Gap (eV)':<15} {'Energy Above Hull (eV/atom)':<20} {'Density (g/cm³)':<15}")
for row in summary_table:
    print(f"{row[0]:<20} {row[1]:<30} {row[2]:<15} {row[3]:<20} {row[4]:<15}")

# Regenerate selected plots
regenerate_plot_ids = ["plot_2", "plot_4", "plot_6"]

for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    title = plot_spec['title']
    description = plot_spec['description']
    plot_type = plot_spec['plot_type']
    axes = plot_spec['axes']

    slug = title.lower().replace(' ', '_')
    filename = f"{plot_id}_{slug}.png"
    out_path = os.path.join('plots_v2', filename)

    # Only regenerate specified plots
    if plot_id not in regenerate_plot_ids:
        continue

    # Prepare data for plotting
    if plot_type == "scatter_2d":
        if plot_id == "plot_2":  # Density vs Band Gap
            x_data = [material.get(axes['x']) for material in mp_results if axes['x'] in material]
            y_data = [material.get(axes['y']) for material in mp_results if axes['y'] in material]
            if x_data and y_data and len(x_data) == len(y_data):
                plt.figure()
                plt.scatter(x_data, y_data, alpha=0.6, edgecolors='w', s=20)
                plt.xlabel("Density (g/cm³)")
                plt.ylabel("Band Gap (eV)")
                plt.title(title)
                plt.grid(True)
            else:
                plt.figure()
                plt.text(0.5, 0.5, 'Insufficient data', ha='center', va='center')
                plt.title(f"{title} - Insufficient Data")

            plt.savefig(out_path)
            if not os.path.exists(out_path):
                raise RuntimeError("Plot was not saved properly.")
            plt.close()

    elif plot_type == "histogram":
        if plot_id == "plot_4":  # Histogram of Density
            x_data = [material.get(axes['x']) for material in mp_results if axes['x'] in material]
            if x_data:
                plt.figure()
                plt.hist(x_data, bins=10, alpha=0.7)
                plt.xlabel("Density (g/cm³)")
                plt.ylabel("Count")
                plt.title(title)
                plt.grid(axis='y', alpha=0.75)
            else:
                plt.figure()
                plt.text(0.5, 0.5, 'Insufficient data', ha='center', va='center')
                plt.title(f"{title} - Insufficient Data")

            plt.savefig(out_path)
            if not os.path.exists(out_path):
                raise RuntimeError("Plot was not saved properly.")
            plt.close()

    elif plot_type == "scatter_3d":
        if plot_id == "plot_6":  # 3D Scatter of Band Gap, Density, and Energy Above Hull
            x_data = [material.get(axes['x']) for material in mp_results if axes['x'] in material]
            y_data = [material.get(axes['y']) for material in mp_results if axes['y'] in material]
            z_data = [material.get(axes['z']) for material in mp_results if axes['z'] in material]
            if x_data and y_data and z_data and len(x_data) == len(y_data) == len(z_data):
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                ax.scatter(x_data, y_data, z_data, alpha=0.6, edgecolors='w')
                ax.set_xlabel("Band Gap (eV)")
                ax.set_ylabel("Density (g/cm³)")
                ax.set_zlabel("Energy Above Hull (eV/atom)")
                plt.title(title)
            else:
                plt.figure()
                plt.text(0.5, 0.5, 'Insufficient data', ha='center', va='center')
                plt.title(f"{title} - Insufficient Data")

            plt.savefig(out_path)
            if not os.path.exists(out_path):
                raise RuntimeError("Plot was not saved properly.")
            plt.close()

# Write the V2 plot manifest
v2_manifest = {
    "plots_v2": []
}

for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    title = plot_spec['title']
    description = plot_spec['description']
    slug = title.lower().replace(' ', '_')
    filename = f"{plot_id}_{slug}.png"
    rel_path = os.path.join('plots_v2', filename)

    if plot_id in regenerate_plot_ids:
        v2_manifest["plots_v2"].append({
            "plot_id": plot_id,
            "name": filename,
            "path": rel_path,
            "description": description
        })

# Write V2 manifest file atomically
v2_manifest_temp_path = 'plots_v2_manifest.json.tmp'
v2_manifest_final_path = 'plots_v2_manifest.json'
with open(v2_manifest_temp_path, 'w') as f:
    json.dump(v2_manifest, f, indent=2)
os.replace(v2_manifest_temp_path, v2_manifest_final_path)
