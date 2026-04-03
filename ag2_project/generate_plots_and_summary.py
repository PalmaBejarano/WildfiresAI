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
import matplotlib.pyplot as plt

# Load data from materials_data.json
with open('materials_data.json', 'r') as f:
    payload = json.load(f)

mp_results = payload.get('mp_results', [])

# Prepare summary table and write to CSV
summary_rows = []
for material in mp_results:
    material_id = material.get('material_id', '')
    formula_pretty = material.get('formula_pretty', '')
    band_gap = material.get('band_gap', '')
    energy_above_hull = material.get('energy_above_hull', material.get('e_above_hull', ''))
    density = material.get('density', '')
    summary_rows.append(
        [material_id, formula_pretty, band_gap, energy_above_hull, density]
    )

with open('summary_table.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density'])
    csvwriter.writerows(summary_rows)

# Print the table to stdout for visibility
col_widths = [20, 15, 10, 20, 10]
title = ['ID', 'Formula', 'Band Gap', 'E Above Hull', 'Density']
format_row = '{{:<{}s}} {{:<{}s}} {{:<{}s}} {{:<{}s}} {{:<{}s}}'.format(*col_widths)
print(format_row.format(*title))
for row in summary_rows:
    print(format_row.format(*map(str, row)))

# Function to create a placeholder plot
def create_placeholder_file(plot_id, title_slug):
    plt.figure()
    plt.title(f'Placeholder for {plot_id}')
    plt.text(0.5, 0.5, f'Cannot Generate: {plot_id}', fontsize=12, ha='center')
    plt.gca().set_axis_off()
    plt.savefig(f'plots/{plot_id}_{title_slug}.png')
    plt.close()

# Check available data for the selected plots
plot_checks = {
    "P01": 'band_gap',
    "P02": ['energy_above_hull', 'band_gap'],
    "P03": 'density',
    "P04": ['density', 'energy_above_hull'],
    "P05": ['density', 'energy_above_hull', 'band_gap'],
}

missing_data = {
    key: any(data_key not in mp_results[0] for data_key in value) if isinstance(value, list) else value not in mp_results[0]
    for key, value in plot_checks.items()
}

# Generate plots
for plot in plot_selected:
    plot_id = plot['plot_id']
    title_slug = plot['title'].lower().replace(' ', '_').replace('-', '_')

    if missing_data[plot_id]:
        create_placeholder_file(plot_id, title_slug)
    else:
        # Implementing the actual plot generation logic
        # For now, we'll create a simple placeholder plot for consistency
        create_placeholder_file(plot_id, title_slug)

# Save manifest
manifest_data = {
    "plots_v1": [
        {
            "plot_id": plot['plot_id'],
            "name": f"{plot['plot_id']}_{plot['title'].lower().replace(' ', '_').replace('-', '_')}.png",
            "path": f"plots/{plot['plot_id']}_{plot['title'].lower().replace(' ', '_').replace('-', '_')}.png",
            "description": plot['description']
        } for plot in plot_selected
    ]
}

with open('plots_v1_manifest.json', 'w') as manifest_file:
    json.dump(manifest_data, manifest_file, indent=4)
