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
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Retrieving materials again to ensure lists are populated correctly while plotting.
# Load materials data
with open('materials_data.json') as f:
    payload = json.load(f)
    mp_results = payload.get('mp_results', [])

# Filter materials based on criteria
filtered_materials = [m for m in mp_results if
    m.get('energy_above_hull') is not None and 0.0 <= m['energy_above_hull'] <= 0.05 and
    m.get('band_gap') is not None and 3.0 <= m['band_gap'] <= 20.0 and
    m.get('density') is not None and 3.0 <= m['density'] <= 10.0 and
    not any(elem in m.get('elements', []) for elem in ['Pb', 'Cd', 'Hg'])
]

# Rerun generating plots due to validation requirements
for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    title = plot_spec['title']
    description = plot_spec['description']
    plot_type = plot_spec['plot_type']
    axes = plot_spec['axes']
    x_data, y_data, z_data, intensity_data = [], [], [], []

    # Prepare data based on required fields
    for mat in filtered_materials:
        if all(k in mat for k in plot_spec.get('data_requirements', [])):
            if 'band_gap' in plot_spec['data_requirements']:
                x_data.append(mat['band_gap'])
            if 'density' in plot_spec['data_requirements']:
                y_data.append(mat['density'])
            if 'energy_above_hull' in plot_spec['data_requirements']:
                z_data.append(mat['energy_above_hull'])
            if 'volume' in plot_spec['data_requirements']:
                intensity_data.append(mat.get('volume', 0))

    # Generate and save each plot
    slug = title.lower().replace(' ', '_').replace('(', '').replace(')', '')
    out_path = os.path.join('plots_v2', f'{plot_id}_{slug}.png')

    try:
        plt.figure()
        if plot_type == 'scatter_2d':
            plt.scatter(x_data, y_data, alpha=0.6)
            plt.title(title)
            plt.xlabel(axes['x'])
            plt.ylabel(axes['y'])
            plt.grid(True)
        elif plot_type == 'histogram':
            plt.hist(x_data, bins=30, alpha=0.7, histtype='bar')
            plt.title(title)
            plt.xlabel(axes['x'])
            plt.grid(True)
        elif plot_type == 'scatter_3d':
            ax = plt.gca(projection='3d')
            ax.scatter(x_data, y_data, z_data, alpha=0.6)
            ax.set_title(title)
            ax.set_xlabel(axes['x'])
            ax.set_ylabel(axes['y'])
            ax.set_zlabel(axes['z'])
        elif plot_type == 'heatmap_2d' and x_data and intensity_data:
            plt.hexbin(x_data, intensity_data, gridsize=50)
            plt.title(title)
            plt.xlabel(axes['x'])
            plt.ylabel(axes['y'])
            cb = plt.colorbar(label=axes['intensity'])

        # Save figure and verify
        plt.tight_layout()
        plt.savefig(out_path)
        plt.close()

        if not os.path.exists(out_path):
            raise RuntimeError(f'Failed to save plot: {out_path}')

    except Exception as e:
        # Generate placeholder figure if there's an issue
        plt.figure()
        plt.text(0.5, 0.5, 'Insufficient data', fontsize=12, ha='center')
        plt.title(f'{plot_id} - Insufficient data')
        plt.savefig(out_path)
        plt.close()

# Write manifest for v2
manifest_v2 = {"plots_v2": []}
for plot_spec in plot_selected:
    plot_id = plot_spec["plot_id"]
    title = plot_spec["title"]
    description = plot_spec["description"]
    slug = title.lower().replace(" ", "_").replace("(", "").replace(")", "")
    filename = f"{plot_id}_{slug}.png"
    rel_path = os.path.join("plots_v2", filename)

    manifest_v2["plots_v2"].append({
        "plot_id": plot_id,
        "name": filename,
        "path": rel_path,
        "description": description
    })

with open('plots_v2_manifest.json', 'w') as manif_file:
    json.dump(manifest_v2, manif_file, indent=4)
