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
import csv
import os
import matplotlib.pyplot as plt

# Load the data
with open('materials_data.json', 'r') as f:
    payload = json.load(f)
    mp_results = payload.get('mp_results', [])

# Prepare the summary table
summary_data = []
for result in mp_results:
    # Collect necessary fields with fallbacks for missing data
    material_id = result.get('material_id', '')
    formula_pretty = result.get('formula_pretty', '')
    band_gap = result.get('band_gap', '')
    energy_above_hull = result.get('energy_above_hull', result.get('e_above_hull', ''))
    density = result.get('density', '')

    # Append to summary data
    summary_data.append([material_id, formula_pretty, band_gap, energy_above_hull, density])

# Export summary table to CSV
with open('summary_table.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density'])
    writer.writerows(summary_data)

# Print the summary table
print("Summary Table:\n")
print("{:<15} {:<20} {:<10} {:<18} {:<10}".format('Material ID', 'Formula', 'Band Gap', 'Energy Above Hull', 'Density'))
for row in summary_data:
    print("{:<15} {:<20} {:<10} {:<18} {:<10}".format(*row))

# Check if plot_selected exists
if 'plot_selected' in locals() and plot_selected:
    for plot_spec in plot_selected:
        plot_id = plot_spec['plot_id']
        title = plot_spec['title']
        description = plot_spec['description']
        data_requirements = plot_spec['data_requirements']
        axes = plot_spec['axes']
        plot_type = plot_spec['plot_type']

        # Determine if required data is available
        data_available = all(req in mp_results[0] for req in data_requirements) if mp_results else False

        # Prepare the slug for file naming
        slug = title.lower().replace(' ', '_')
        out_path = os.path.join("plots", f"{plot_id}_{slug}.png")

        plt.figure()
        if data_available:
            # Extract relevant data
            if plot_type == 'scatter_2d':
                x = [result[axes['x']] for result in mp_results]
                y = [result[axes['y']] for result in mp_results]
                plt.scatter(x, y)
                plt.xlabel(axes['x'])
                plt.ylabel(axes['y'])
            elif plot_type == 'histogram':
                data = [result[data_requirements[0]] for result in mp_results]
                plt.hist(data, bins=30)
                plt.xlabel(axes['x'])
            # Other plot types could be handled here

            plt.title(title)
            plt.savefig(out_path)
            plt.close()
        else:
            # Placeholder plot
            plt.title(f"{plot_id}: {title}")
            plt.text(0.5, 0.5, 'Insufficient data', ha='center', va='center', fontsize=12)
            plt.savefig(out_path)
            plt.close()

        # Verify that plot was saved
        if not os.path.exists(out_path):
            raise RuntimeError(f"Failed to save plot {out_path}")

# Create a manifest of plots
manifest = {"plots_v1": []}
for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    title = plot_spec['title']
    slug = title.lower().replace(' ', '_')
    filename = f"{plot_id}_{slug}.png"
    manifest_entry = {
        "plot_id": plot_id,
        "name": filename,
        "path": os.path.join("plots", filename),
        "description": plot_spec['description']
    }
    manifest["plots_v1"].append(manifest_entry)

# Write manifest to file
with open('plots_v1_manifest.json', 'w') as manifest_file:
    json.dump(manifest, manifest_file, indent=4)
