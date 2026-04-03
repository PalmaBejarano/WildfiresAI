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

# Load materials data
def load_materials():
    with open('materials_data.json', 'r') as f:
        payload = json.load(f)
    return payload.get('mp_results', [])

# Export summary table to CSV
def export_summary_table_to_csv(mp_results):
    # Define the csv file header
    header = ['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density']
    with open('summary_table.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        # Write the data
        for material in mp_results:
            writer.writerow([
                material.get('material_id'),
                material.get('formula_pretty'),
                material.get('band_gap', ''),
                material.get('energy_above_hull', material.get('e_above_hull', '')),
                material.get('density', '')
            ])

# Print readable table to stdout
def print_summary_table(mp_results):
    header = ['Material ID', 'Formula', 'Band Gap', 'Energy Above Hull', 'Density']
    rows = []
    for material in mp_results:
        rows.append([
            material.get('material_id'),
            material.get('formula_pretty'),
            material.get('band_gap', ''),
            material.get('energy_above_hull', material.get('e_above_hull', '')),
            material.get('density', '')
        ])
    # Calculate column widths for pretty printing
    col_widths = [max(len(str(item)) for item in column) for column in zip(*[header] + rows)]
    # Create a format string for the rows
    row_format = '  '.join(['{:<{}}'.format(str(item), col_width) for item, col_width in zip(header, col_widths)])
    print(row_format.format(*header))
    for row in rows:
        print(row_format.format(*row))

# Execute functions
def main():
    mp_results = load_materials()
    export_summary_table_to_csv(mp_results)
    print_summary_table(mp_results)

if __name__ == "__main__":
    main()
