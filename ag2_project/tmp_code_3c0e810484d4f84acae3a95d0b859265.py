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

with open('materials_data.json') as f:
    payload = json.load(f)
    mp_results = payload.get('mp_results', [])

# Filter materials
materials = []
for material in mp_results:
    energy_above_hull = material.get('energy_above_hull', material.get('e_above_hull', None))
    if all(e not in material.get('elements', []) for e in ['Pb', 'Cd', 'Hg']):
        if (0.0 <= energy_above_hull <= 0.05 and
            3.0 <= material.get('band_gap', -1) <= 20.0 and
            3.0 <= material.get('density', -1) <= 10.0):
            materials.append(material)

# List of plots to be regenerated based on validation
plots_to_regenerate = ['plot_1', 'plot_2', 'plot_3', 'plot_4', 'plot_5']

# Ensure plots_v2 exists
os.makedirs('plots_v2', exist_ok=True)

# Generate Test Plots with placebo if data is missing
manifest_v2 = []

for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    if plot_id not in plots_to_regenerate:
        continue

    title = plot_spec['title']
    description = plot_spec['description']
    plot_type = plot_spec['plot_type']
    axes = plot_spec['axes']

    if plot_type == "scatter_2d":
        x_data = [material.get(axes['x'], None) for material in materials]
        y_data = [material.get(axes['y'], None) for material in materials]
        plt.figure()

        if all(v is not None for v in x_data + y_data):
            plt.scatter(x_data, y_data, edgecolor='k', alpha=0.7)
            plt.xlabel(axes['x'].replace('_', ' ').title() + ' (units)')
            plt.ylabel(axes['y'].replace('_', ' ').title() + ' (units)')
        else:
            plt.text(0.5, 0.5, "Insufficient data", ha='center')
        plt.title(title)
        plt.grid(True)

    elif plot_type == "histogram":
        hist_data = [material.get(axes['x'], None) for material in materials]
        plt.figure()
        if all(v is not None for v in hist_data):
            plt.hist(hist_data, bins=20, edgecolor='k')
            plt.xlabel(axes['x'].replace('_', ' ').title() + ' (units)')
        else:
            plt.text(0.5, 0.5, "Insufficient data", ha='center')
        plt.title(title)
        plt.grid(axis='y')
    else:
        plt.figure()
        plt.text(0.5, 0.5, "Insufficient data", ha='center')
        plt.title(f"Placeholder for {title}")

    plt.tight_layout()
    out_path = os.path.join("plots_v2", f"{plot_id}_{title.replace(' ', '_')}.png")
    plt.savefig(out_path)
    assert os.path.exists(out_path)
    plt.close()

    manifest_v2.append({
        "plot_id": plot_id,
        "name": title,
        "path": out_path,
        "description": description
    })

# Save manifest
manifest_path_v2 = "plots_v2_manifest.json"
with open(manifest_path_v2, "w") as f:
    json.dump(manifest_v2, f, indent=4)
