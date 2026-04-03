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
import numpy as np
import csv

# Load materials data
with open('materials_data.json') as f:
    payload = json.load(f)
    mp_results = payload.get("mp_results", [])

# Determine regeneration mode
is_v2 = isinstance(plots_to_regenerate, list) and len(plots_to_regenerate) > 0

# Setup paths and filenames for outputs
v1_manifest_path = "plots_v1_manifest.json"
v2_manifest_path = "plots_v2_manifest.json"
v1_plot_dir = "plots"
v2_plot_dir = "plots_v2"

# Create necessary directories
os.makedirs(v1_plot_dir, exist_ok=True)
os.makedirs(v2_plot_dir, exist_ok=True)

# Define CSV output
csv_file = "summary_table.csv"

# Prepare CSV data
csv_data = []
for material in mp_results:
    material_id = material.get('material_id')
    formula_pretty = material.get('formula_pretty')
    band_gap = material.get('band_gap')
    energy_above_hull = material.get('energy_above_hull', material.get('e_above_hull'))
    density = material.get('density')
    csv_data.append((material_id, formula_pretty, band_gap, energy_above_hull, density))

# Write CSV
with open(csv_file, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density'])
    csvwriter.writerows(csv_data)

# Print table
print(f"{'Material ID':<15} {'Formula':<20} {'Band Gap (eV)':<15} {'Energy Above Hull (eV/atom)':<30} {'Density (g/cm³)':<20}")
for row in csv_data:
    print(f"{row[0]:<15} {row[1]:<20} {row[2]:<15} {row[3]:<30} {row[4]:<20}")

# Initialize manifest list
manifest = []

# Plot generation loop
for plot_spec in plot_selected:
    plot_id = plot_spec["plot_id"]
    title = plot_spec["title"]
    description = plot_spec["description"]
    plot_type = plot_spec["plot_type"]
    axes = plot_spec["axes"]

    # Determine output folder and manifest based on mode
    if is_v2:
        if plot_id not in plots_to_regenerate:
            continue
        output_dir = v2_plot_dir
        manifest_path = v2_manifest_path
    else:
        output_dir = v1_plot_dir
        manifest_path = v1_manifest_path

    # Determine the slug for the filename
    slug = title.lower().replace(" ", "_").replace(",", "")
    out_path = os.path.join(output_dir, f"{plot_id}_{slug}.png")

    if plot_type == "scatter_2d":
        x_values = []
        y_values = []
        for material in mp_results:
            x_value = material.get(axes["x"])
            y_value = material.get(axes["y"])
            if x_value is not None and y_value is not None:
                x_values.append(x_value)
                y_values.append(y_value)
        if x_values and y_values:
            plt.figure()
            plt.scatter(x_values, y_values)
            plt.xlabel(axes["x"].replace('_', ' ').title() + " (eV)")
            plt.ylabel(axes["y"].replace('_', ' ').title() + " (eV)")
            plt.title(title)
            plt.grid(True)
            plt.savefig(out_path)
            plt.close()
        else:
            plt.figure()
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
            plt.savefig(out_path)
            plt.close()
        assert os.path.exists(out_path)
        manifest.append({"plot_id": plot_id, "name": os.path.basename(out_path), "path": out_path, "description": description})
    elif plot_type == "histogram":
        hist_data = [material.get(axes["x"]) for material in mp_results if material.get(axes["x"]) is not None]
        if hist_data:
            plt.figure()
            plt.hist(hist_data, bins=20, alpha=0.7)
            plt.xlabel(axes["x"].replace('_', ' ').title() + " (eV)")
            plt.title(title)
            plt.grid(True)
            plt.savefig(out_path)
            plt.close()
        else:
            plt.figure()
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
            plt.savefig(out_path)
            plt.close()
        assert os.path.exists(out_path)
        manifest.append({"plot_id": plot_id, "name": os.path.basename(out_path), "path": out_path, "description": description})

# Write manifest
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)
