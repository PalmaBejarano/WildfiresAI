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
import pandas as pd

# Load materials data from materials_data.json
with open('materials_data.json') as f:
    payload = json.load(f)
    mp_results = payload.get("mp_results", [])

# Prepare the CSV summary table
data_summary = []
for material in mp_results:
    material_id = material.get('material_id')
    formula = material.get('formula_pretty')
    band_gap = material.get('band_gap')
    energy_above_hull = material.get('energy_above_hull', material.get('e_above_hull'))
    density = material.get('density')
    data_summary.append({
        'material_id': material_id,
        'formula_pretty': formula,
        'band_gap': band_gap,
        'energy_above_hull': energy_above_hull,
        'density': density
    })

# Write the summary table to CSV
summary_df = pd.DataFrame(data_summary)
summary_df.to_csv('summary_table.csv', index=False)

# Print a readable fixed-width table
table_str = summary_df.to_string(index=False)
print(table_str)

# Generate plots
manifest = []
for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    title = plot_spec['title']
    description = plot_spec['description']
    plot_type = plot_spec['plot_type']
    axes = plot_spec['axes']

    out_path = os.path.join("plots", f"{plot_id}_{title.replace(' ', '_')}.png")

    if plot_type == "scatter_2d":
        x_data = [material.get(axes['x']) for material in mp_results if material.get(axes['x']) is not None]
        y_data = [material.get(axes['y']) for material in mp_results if material.get(axes['y']) is not None]

        if x_data and y_data:
            plt.figure()
            plt.scatter(x_data, y_data, alpha=0.5)
            plt.xlabel(axes['x'].replace('_', ' ').title() + ' (eV)')
            plt.ylabel(axes['y'].replace('_', ' ').title() + ' (eV)')
            plt.grid(True)
            plt.title(title)
            plt.xlim(min(x_data) - 0.5, max(x_data) + 0.5)
            plt.ylim(min(y_data) - 0.01, max(y_data) + 0.01)
            plt.savefig(out_path)
            plt.close()
        else:
            plt.figure()
            plt.text(0.5, 0.5, 'Insufficient data', fontsize=12, ha='center')
            plt.title(f"{title} (ID: {plot_id})")
            plt.savefig(out_path)
            plt.close()

    elif plot_type == "histogram":
        hist_data = [material.get(axes['x']) for material in mp_results if material.get(axes['x']) is not None]
        if hist_data:
            plt.figure()
            plt.hist(hist_data, bins=20, edgecolor='black', alpha=0.7)
            plt.xlabel(axes['x'].replace('_', ' ').title() + ' (eV)')
            plt.ylabel('Frequency')
            plt.title(title)
            plt.grid(True)
            plt.savefig(out_path)
            plt.close()

    # Verify file existence
    assert os.path.exists(out_path)

    # Add to manifest
    manifest.append({
        'plot_id': plot_id,
        'name': title,
        'path': out_path,
        'description': description
    })

# Write plots_v1_manifest.json
with open('plots_v1_manifest.json', 'w') as manifest_file:
    json.dump(manifest, manifest_file, indent=2)
