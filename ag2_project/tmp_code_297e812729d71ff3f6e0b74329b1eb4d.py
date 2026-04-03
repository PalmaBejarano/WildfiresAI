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

import os
import json
import matplotlib.pyplot as plt
import numpy as np

# Load materials data
with open('materials_data.json') as f:
    payload = json.load(f)
    mp_results = payload.get('mp_results', [])

# Prepare CSV table
csv_headers = ['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density']
summary_table_data = []
for material in mp_results:
    material_id = material.get('material_id', 'N/A')
    formula_pretty = material.get('formula_pretty', 'N/A')
    band_gap = material.get('band_gap', 'N/A')
    energy_above_hull = material.get('energy_above_hull', material.get('e_above_hull', 'N/A'))
    density = material.get('density', 'N/A')
    summary_table_data.append([material_id, formula_pretty, band_gap, energy_above_hull, density])

# Write summary_table.csv
with open('summary_table.csv', 'w') as f:
    f.write(','.join(csv_headers) + '\n')
    for row in summary_table_data:
        f.write(','.join(map(str, row)) + '\n')

# Print readable fixed-width table
print('{:<15} {:<20} {:<10} {:<20} {:<10}'.format(*csv_headers))
for row in summary_table_data:
    print('{:<15} {:<20} {:<10} {:<20} {:<10}'.format(*row))

# Manifest lists
plots_v1_manifest = []
plots_v2_manifest = []

# Check for regeneration mode
is_v2 = isinstance(plots_to_regenerate, list) and len(plots_to_regenerate) > 0

# Plot generation
for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    title = plot_spec['title']
    description = plot_spec['description']
    plot_type = plot_spec['plot_type']
    axes = plot_spec['axes']

    slug = title.lower().replace(' ', '_')
    if is_v2:
        if plot_id not in plots_to_regenerate:
            continue
        out_path = os.path.join("plots_v2", f"{plot_id}_{slug}.png")
    else:
        out_path = os.path.join("plots", f"{plot_id}_{slug}.png")

    # Scatter plots
    if plot_type == 'scatter_2d':
        x_data = [m.get(axes['x'], None) for m in mp_results]
        y_data = [m.get(axes['y'], None) for m in mp_results]
        x_data, y_data = zip(*[(x, y) for x, y in zip(x_data, y_data) if x is not None and y is not None])
        plt.figure()
        plt.scatter(x_data, y_data)
        plt.xlabel(axes['x'].replace('_', ' ').title())
        plt.ylabel(axes['y'].replace('_', ' ').title())
        plt.title(title)

    # Histogram
    elif plot_type == 'histogram':
        hist_data = [m.get(axes['x'], None) for m in mp_results if m.get(axes['x'], None) is not None]
        plt.figure()
        plt.hist(hist_data, bins=20, edgecolor='k')
        plt.xlabel(axes['x'].replace('_', ' ').title())
        plt.title(title)

    # Placeholder for unsupported plot types
    else:
        plt.figure()
        plt.title(f"{plot_id} - Insufficient data")
        plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")

    plt.savefig(out_path)
    assert os.path.exists(out_path)
    plt.close()

    manifest = {'plot_id': plot_id, 'name': f'{plot_id}_{slug}.png', 'path': out_path, 'description': description}
    if is_v2:
        plots_v2_manifest.append(manifest)
    else:
        plots_v1_manifest.append(manifest)

# Write manifest
if is_v2:
    with open('plots_v2_manifest.json', 'w') as f:
        json.dump(plots_v2_manifest, f, indent=2)
else:
    with open('plots_v1_manifest.json', 'w') as f:
        json.dump(plots_v1_manifest, f, indent=2)
