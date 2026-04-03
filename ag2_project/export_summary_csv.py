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

# Load materials data from the JSON file
with open('materials_data.json', 'r') as f:
    payload = json.load(f)
    mp_results = payload.get("mp_results", [])

# Define the CSV file header
csv_header = ['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density']

# Open the CSV for writing
with open('summary_table.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(csv_header)  # Write the header

    # Write each material's data to the CSV
    for material in mp_results:
        material_id = material.get('material_id', '')
        formula_pretty = material.get('formula_pretty', '')
        band_gap = material.get('band_gap', '')
        energy_above_hull = material.get('energy_above_hull', '')
        if not energy_above_hull:  # Attempt to use alternative field name if available
            energy_above_hull = material.get('e_above_hull', '')
        density = material.get('density', '')
        csvwriter.writerow([material_id, formula_pretty, band_gap, energy_above_hull, density])

# Print the results to stdout in a neat format
print("{:<15} {:<25} {:<10} {:<20} {:<10}".format(*csv_header))
for material in mp_results:
    material_id = material.get('material_id', '')
    formula_pretty = material.get('formula_pretty', '')
    band_gap = material.get('band_gap', '')
    energy_above_hull = material.get('energy_above_hull', '')
    if not energy_above_hull:
        energy_above_hull = material.get('e_above_hull', '')
    density = material.get('density', '')
    print("{:<15} {:<25} {:<10} {:<20} {:<10}".format(material_id, formula_pretty, band_gap, energy_above_hull, density))
