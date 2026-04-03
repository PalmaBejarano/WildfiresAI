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

# Iterate over selected plots
for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    title = plot_spec['title']
    description = plot_spec['description']
    plot_type = plot_spec['plot_type']
    axes = plot_spec['axes']

    slug = title.lower().replace(' ', '_')
    filename = f"{plot_id}_{slug}.png"
    out_path = os.path.join('plots', filename)

    # Prepare data for plotting
    if plot_type == "scatter_2d":
        x_data = [material.get(axes['x']) for material in mp_results if axes['x'] in material]
        y_data = [material.get(axes['y']) for material in mp_results if axes['y'] in material]
        if x_data and y_data and len(x_data) == len(y_data):
            plt.figure()
            plt.scatter(x_data, y_data)
            plt.xlabel(f"{axes['x'].replace('_', ' ').title()} (eV)")
            plt.ylabel(f"{axes['y'].replace('_', ' ').title()} (eV)")
            plt.title(title)
        else:
            plt.figure()
            plt.text(0.5, 0.5, 'Insufficient data', ha='center', va='center')
            plt.title(f"{title} - Insufficient Data")

        plt.savefig(out_path)
        if not os.path.exists(out_path):
            raise RuntimeError("Plot was not saved properly.")
        plt.close()

    elif plot_type == "histogram":
        x_data = [material.get(axes['x']) for material in mp_results if axes['x'] in material]
        if x_data:
            plt.figure()
            plt.hist(x_data, bins=10)
            plt.xlabel(f"{axes['x'].replace('_', ' ').title()} (eV)")
            plt.title(title)
        else:
            plt.figure()
            plt.text(0.5, 0.5, 'Insufficient data', ha='center', va='center')
            plt.title(f"{title} - Insufficient Data")

        plt.savefig(out_path)
        if not os.path.exists(out_path):
            raise RuntimeError("Plot was not saved properly.")
        plt.close()

    elif plot_type == "scatter_3d":
        x_data = [material.get(axes['x']) for material in mp_results if axes['x'] in material]
        y_data = [material.get(axes['y']) for material in mp_results if axes['y'] in material]
        z_data = [material.get(axes['z']) for material in mp_results if axes['z'] in material]
        if x_data and y_data and z_data and len(x_data) == len(y_data) == len(z_data):
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(x_data, y_data, z_data)
            ax.set_xlabel(f"{axes['x'].replace('_', ' ').title()} (eV)")
            ax.set_ylabel(f"{axes['y'].replace('_', ' ').title()} (eV)")
            ax.set_zlabel(f"{axes['z'].replace('_', ' ').title()} (eV)")
            plt.title(title)
        else:
            plt.figure()
            plt.text(0.5, 0.5, 'Insufficient data', ha='center', va='center')
            plt.title(f"{title} - Insufficient Data")

        plt.savefig(out_path)
        if not os.path.exists(out_path):
            raise RuntimeError("Plot was not saved properly.")
        plt.close()

    else:
        plt.figure()
        plt.text(0.5, 0.5, 'Unsupported Plot Type', ha='center', va='center')
        plt.title(f"{title} - Unsupported Plot Type")
        plt.savefig(out_path)
        plt.close()

# Write the V1 plot manifest
v1_manifest = {
    "plots_v1": []
}

for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    title = plot_spec['title']
    description = plot_spec['description']
    slug = title.lower().replace(' ', '_')
    filename = f"{plot_id}_{slug}.png"
    rel_path = os.path.join('plots', filename)

    v1_manifest["plots_v1"].append({
        "plot_id": plot_id,
        "name": filename,
        "path": rel_path,
        "description": description
    })

# Write manifest file atomically
manifest_temp_path = 'plots_v1_manifest.json.tmp'
manifest_final_path = 'plots_v1_manifest.json'
with open(manifest_temp_path, 'w') as f:
    json.dump(v1_manifest, f, indent=2)
os.replace(manifest_temp_path, manifest_final_path)
