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
import pandas as pd

# Load data from materials_data.json
with open('materials_data.json', 'r') as f:
    data = json.load(f)

mp_results = data.get('mp_results', [])

# Create a DataFrame
materials_df = pd.DataFrame(mp_results)

# Filter materials based on criteria
filtered_df = materials_df[
    (materials_df['energy_above_hull'].between(0.0, 0.05)) &
    (materials_df['band_gap'].between(3.0, 20.0)) &
    (materials_df['density'].between(3.0, 10.0)) &
    (~materials_df['elements'].apply(lambda x: any(elem in ['Pb', 'Cd', 'Hg'] for elem in x)))
]

# Export summary table to summary_table.csv
filtered_df[['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density']].to_csv('summary_table.csv', index=False)

# Print readable table
print(filtered_df[['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density']])

# Create plots directory
os.makedirs('plots', exist_ok=True)

plot_selected = [
    {"plot_id": "plot_1", "title": "Energy Above Hull Distribution", "description": "Histogram showing...", "axes": {"x": "energy_above_hull"}, "plot_type": "histogram"},
    {"plot_id": "plot_2", "title": "Band Gap vs Density", "description": "Scatter plot of...", "axes": {"x": "band_gap", "y": "density"}, "plot_type": "scatter_2d"},
    {"plot_id": "plot_4", "title": "Density Distribution Histogram", "description": "Histogram showing...", "axes": {"x": "density"}, "plot_type": "histogram"},
    {"plot_id": "plot_5", "title": "Material Stability vs. Band Gap", "description": "Scatter plot showing...", "axes": {"x": "energy_above_hull", "y": "band_gap"}, "plot_type": "scatter_2d"},
    {"plot_id": "plot_7", "title": "Density vs Energy Above Hull", "description": "Scatter plot to...", "axes": {"x": "density", "y": "energy_above_hull"}, "plot_type": "scatter_2d"}
]

# Generate plots
for plot_spec in plot_selected:
    plot_id = plot_spec['plot_id']
    title = plot_spec['title']
    plot_type = plot_spec['plot_type']
    axes = plot_spec['axes']

    slug = title.lower().replace(' ', '_')
    out_path = os.path.join('plots', f'{plot_id}_{slug}.png')

    fig, ax = plt.subplots()
    if plot_type == 'histogram':
        ax.hist(filtered_df[axes['x']].dropna(), bins=30, color='blue', alpha=0.7)
        ax.set_xlabel(axes['x'])
        ax.set_ylabel('Frequency')
    elif plot_type == 'scatter_2d':
        ax.scatter(filtered_df[axes['x']], filtered_df[axes['y']], alpha=0.7)
        ax.set_xlabel(axes['x'])
        ax.set_ylabel(axes['y'])
    else:
        ax.text(0.5, 0.5, 'Insufficient data', fontsize=12, ha='center')
    ax.set_title(title)
    plt.savefig(out_path)
    if not os.path.exists(out_path):
        raise RuntimeError(f'Plot {out_path} could not be saved.')
    plt.close()

# Write the V1 manifest
manifest = {
    "plots_v1": [
        {"plot_id": spec['plot_id'], "name": f"{spec['plot_id']}_{spec['title'].lower().replace(' ', '_')}.png", "path": f"plots/{spec['plot_id']}_{spec['title'].lower().replace(' ', '_')}.png", "description": spec['description']}
        for spec in plot_selected
    ]
}
with open('plots_v1_manifest.json.tmp', 'w') as f:
    json.dump(manifest, f, indent=4)
os.replace('plots_v1_manifest.json.tmp', 'plots_v1_manifest.json')
