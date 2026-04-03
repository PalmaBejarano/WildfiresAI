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
import numpy as np
import os

# Assuming the working directory is already PROJECT_FOLDER

# Load data from materials_data.json
with open('materials_data.json', 'r') as f:
    payload = json.load(f)
    mp_results = payload.get("mp_results", [])

# Prepare the data for plotting
material_ids = []
formulas = []
band_gaps = []
energy_above_hulls = []
densities = []

for result in mp_results:
    material_ids.append(result.get("material_id", ""))
    formulas.append(result.get("formula_pretty", ""))
    band_gaps.append(result.get("band_gap", float('nan')))
    energy_above_hulls.append(result.get("e_above_hull", result.get("energy_above_hull", float('nan'))))
    densities.append(result.get("density", float('nan')))

# Export CSV summary table
table_data = zip(material_ids, formulas, band_gaps, energy_above_hulls, densities)
summary_table_path = 'summary_table.csv'
with open(summary_table_path, 'w') as f:
    f.write('material_id,formula_pretty,band_gap,energy_above_hull,density\n')
    for row in table_data:
        f.write(','.join(map(str, row)) + '\n')

# Print a formatted table
print("\nSummary Table:")
print(f"{'Material ID':<15} {'Formula':<15} {'Band Gap (eV)':<15} {'E Above Hull (eV/atom)':<25} {'Density (g/cm³)':<15}")
for row in table_data:
    print(f"{row[0]:<15} {row[1]:<15} {row[2]:<15.2f} {row[3]:<25.2f} {row[4]:<15.2f}")

# Plotting selected plots
plot_selected = [
    {"plot_id": "plot_1", "title": "Band Gap vs Density", "data_requirements": ["band_gap", "density"], "plot_type": "scatter_2d", "axes": {"x": "band_gap", "y": "density"}},
    {"plot_id": "plot_2", "title": "Energy Above Hull Distribution", "data_requirements": ["energy_above_hull"], "plot_type": "histogram", "axes": {"x": "energy_above_hull"}},
    {"plot_id": "plot_5", "title": "Band Gap vs Energy Above Hull", "data_requirements": ["band_gap", "energy_above_hull"], "plot_type": "scatter_2d", "axes": {"x": "band_gap", "y": "energy_above_hull"}},
    {"plot_id": "plot_6", "title": "3D Stability Map", "data_requirements": ["band_gap", "density", "energy_above_hull"], "plot_type": "scatter_3d", "axes": {"x": "band_gap", "y": "density", "z": "energy_above_hull"}},
    {"plot_id": "plot_10", "title": "Comprehensive Property Analysis", "data_requirements": ["band_gap", "density", "energy_above_hull"], "plot_type": "scatter_3d", "axes": {"x": "band_gap", "y": "density", "z": "energy_above_hull"}},
]

for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    title = plot_spec['title']
    plot_type = plot_spec['plot_type']
    x_label = plot_spec['axes']['x']
    y_label = plot_spec['axes'].get('y', '')
    z_label = plot_spec['axes'].get('z', '')

    # Create figure
    fig = plt.figure()

    if plot_type == "scatter_2d":
        plt.scatter(x=band_gaps if x_label == 'band_gap' else energy_above_hulls,
                    y=densities if y_label == 'density' else energy_above_hulls)
        plt.xlabel(x_label.replace('_', ' ').title())
        plt.ylabel(y_label.replace('_', ' ').title())
    elif plot_type == "histogram":
        data = energy_above_hulls if x_label == 'energy_above_hull' else densities
        plt.hist(data, bins=20)
        plt.xlabel(x_label.replace('_', ' ').title())
        plt.ylabel('Frequency')
    elif plot_type == "scatter_3d":
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(
            xs=band_gaps if x_label == 'band_gap' else densities,
            ys=densities if y_label == 'density' else energy_above_hulls,
            zs=energy_above_hulls if z_label == 'energy_above_hull' else densities)
        ax.set_xlabel(x_label.replace('_', ' ').title())
        ax.set_ylabel(y_label.replace('_', ' ').title())
        ax.set_zlabel(z_label.replace('_', ' ').title())
    else:
        # Insufficient data or unrecognized type, create placeholder
        plt.text(0.5, 0.5, 'Insufficient data', horizontalalignment='center',
                 verticalalignment='center', fontsize=12, transform=plt.gca().transAxes)

    plt.title(title)

    # Save the plot
    slug = title.lower().replace(" ", "_").replace(",", "").replace(":", "")
    out_path = os.path.join("plots", f"{plot_id}_{slug}.png")
    plt.savefig(out_path)

    # Validate plot saving
    if not os.path.exists(out_path):
        raise RuntimeError(f"Plot {out_path} could not be saved.")

    plt.close()
