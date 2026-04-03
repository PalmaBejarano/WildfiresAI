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
import numpy as np
import csv

with open('materials_data.json') as f:
    payload = json.load(f)
    mp_results = payload.get('mp_results', [])

# Filter materials based on constraints
materials = []
for material in mp_results:
    energy_above_hull = material.get('energy_above_hull', material.get('e_above_hull', None))
    if not all(e in material.get('elements', []) for e in ['Pb', 'Cd', 'Hg']):
        if (0.0 <= energy_above_hull <= 0.05 and
            3.0 <= material.get('band_gap', -1) <= 20.0 and
            3.0 <= material.get('density', -1) <= 10.0):
            materials.append(material)

# Build CSV
csv_path = 'summary_table.csv'
with open(csv_path, 'w', newline='') as csvfile:
    fieldnames = ['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for material in materials:
        material_id = material.get('material_id', '')
        formula_pretty = material.get('formula_pretty', '')
        band_gap = material.get('band_gap', '')
        energy_above_hull = material.get('energy_above_hull', material.get('e_above_hull', ''))
        density = material.get('density', '')
        writer.writerow({
            'material_id': material_id,
            'formula_pretty': formula_pretty,
            'band_gap': band_gap,
            'energy_above_hull': energy_above_hull,
            'density': density
        })

# Print fixed-width table
print(f"{'Material ID':<15} {'Formula':<10} {'Band Gap (eV)':<15} {'Energy Above Hull (eV/atom)':<30} {'Density (g/cm^3)':<20}")
for material in materials:
    print(f"{material.get('material_id', ''):<15} {material.get('formula_pretty', ''):<10} {material.get('band_gap', ''):<15} {material.get('energy_above_hull', ''):<30} {material.get('density', ''):<20}")

# Generate plots and save manifest
manifest = []
v2_generate = False
plots_to_regenerate = []  # Checks if regeneration mode is active

if os.path.exists('plots_to_regenerate'):
    with open('plots_to_regenerate') as f:
        plots_to_regenerate = json.load(f)
    v2_generate = bool(plots_to_regenerate)

for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    title = plot_spec['title']
    description = plot_spec['description']
    plot_type = plot_spec['plot_type']
    axes = plot_spec['axes']

    if v2_generate and plot_id not in plots_to_regenerate:
        continue

    if plot_type == "scatter_2d":
        x_data = [material.get(axes['x'], None) for material in materials]
        y_data = [material.get(axes['y'], None) for material in materials]

        plt.figure()
        plt.scatter(x_data, y_data)
        plt.xlabel(axes['x'].replace('_', ' ').title())
        plt.ylabel(axes['y'].replace('_', ' ').title())
        plt.title(title)

    elif plot_type == "histogram":
        hist_data = [material.get(axes['x'], None) for material in materials]

        plt.figure()
        plt.hist(hist_data, bins=20)
        plt.xlabel(axes['x'].replace('_', ' ').title())
        plt.title(title)

    else:
        # Placeholder plot for unsupported types
        plt.figure()
        plt.text(0.5, 0.5, "Insufficient data", ha='center')
        plt.title(f"Placeholder for {title}")

    # Save plot
    if v2_generate:
        out_path = os.path.join("plots_v2", f"{plot_id}_{title.replace(' ', '_')}.png")
    else:
        out_path = os.path.join("plots", f"{plot_id}_{title.replace(' ', '_')}.png")

    plt.savefig(out_path)
    assert os.path.exists(out_path)
    plt.close()

    manifest.append({
        "plot_id": plot_id,
        "name": title,
        "path": out_path,
        "description": description
    })

# Write manifest
manifest_path = "plots_v2_manifest.json" if v2_generate else "plots_v1_manifest.json"
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=4)
