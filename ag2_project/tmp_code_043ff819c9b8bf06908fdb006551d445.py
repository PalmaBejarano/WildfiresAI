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

import json
import os
import matplotlib.pyplot as plt
import csv

# Load materials data
with open('materials_data.json', 'r') as f:
    payload = json.load(f)
    mp_results = payload.get("mp_results", [])

# Directories from path configuration
data_processed = PATHS["data_processed"]
plots_v1 = PATHS["plots_v1"]
plots_v2 = PATHS.get("plots_v2")
plots_manifests = PATHS["plots_manifests"]

# Determine if we're in regeneration mode
is_v2 = isinstance(plots_to_regenerate, list) and len(plots_to_regenerate) > 0

# Write summary table
summary_table_path = os.path.join(data_processed, "summary_table.csv")
with open(summary_table_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density'])
    for material in mp_results:
        material_id = material.get('material_id')
        formula_pretty = material.get('formula_pretty')
        band_gap = material.get('band_gap')
        energy_above_hull = material.get('energy_above_hull', material.get('e_above_hull'))
        density = material.get('density')
        writer.writerow([material_id, formula_pretty, band_gap, energy_above_hull, density])

# Print fixed-width table
print("{:<15} {:<20} {:<10} {:<20} {:<10}".format('material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density'))
for material in mp_results:
    material_id = material.get('material_id')
    formula_pretty = material.get('formula_pretty')
    band_gap = material.get('band_gap')
    energy_above_hull = material.get('energy_above_hull', material.get('e_above_hull'))
    density = material.get('density')
    print("{:<15} {:<20} {:<10} {:<20} {:<10}".format(material_id, formula_pretty, band_gap, energy_above_hull, density))

# Plot regeneration
manifest = []
for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    title = plot_spec['title']
    description = plot_spec['description']
    plot_type = plot_spec['plot_type']
    axes = plot_spec['axes']

    # Only regenerate selected plots for v2
    if is_v2 and plot_id not in plots_to_regenerate:
        continue

    # Determine output path
    slug = plot_spec['title'].replace(' ', '_').lower()
    out_path = os.path.join(plots_v2 if is_v2 else plots_v1, f"{plot_id}_{slug}.png")

    if plot_type == "scatter_2d":
        x_data = [material[axes['x']] for material in mp_results if material.get(axes['x']) is not None]
        y_data = [material[axes['y']] for material in mp_results if material.get(axes['y']) is not None]
        if len(x_data) == 0 or len(y_data) == 0:
            plt.figure()
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
        else:
            plt.scatter(x_data, y_data, alpha=0.7)
            plt.title(title)
            plt.xlabel(axes['x'].replace('_', ' ').title() + " (units)")
            plt.ylabel(axes['y'].replace('_', ' ').title() + " (units)")
            plt.grid(True)
    elif plot_type == "histogram":
        hist_data = [material[axes['x']] for material in mp_results if material.get(axes['x']) is not None]
        if len(hist_data) == 0:
            plt.figure()
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
        else:
            plt.hist(hist_data, bins=20, edgecolor='black')
            plt.title(title)
            plt.xlabel(axes['x'].replace('_', ' ').title() + " (units)")
            plt.ylabel('Frequency')
            plt.grid(True)
    else:
        plt.figure()
        plt.title(f"{plot_id} - Insufficient data")
        plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")

    plt.savefig(out_path)
    assert os.path.exists(out_path)
    plt.close()

    # Append to manifest
    manifest.append({
        "plot_id": plot_id,
        "name": os.path.basename(out_path),
        "path": out_path,
        "description": description
    })

# Write manifest for v2
if is_v2:
    manifest_file = os.path.join(plots_manifests, "plots_v2_manifest.json")
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=4)
