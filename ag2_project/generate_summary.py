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

# Load the materials data from materials_data.json
with open("materials_data.json", "r") as f:
    payload = json.load(f)
    mp_results = payload.get("mp_results", [])

# Define the table columns
columns = ["material_id", "formula_pretty", "band_gap", "energy_above_hull", "density"]

data_rows = []
for material in mp_results:
    # Extract the relevant fields, filling missing data with empty values
    row = [
        material.get("material_id", ""),
        material.get("formula_pretty", ""),
        material.get("band_gap", ""),
        material.get("energy_above_hull", material.get("e_above_hull", "")),  # Support alternative field naming
        material.get("density", "")
    ]
    data_rows.append(row)

# Write to CSV
csv_filename = "summary_table.csv"
with open(csv_filename, "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(columns)
    writer.writerows(data_rows)

# Print a clean, readable table to stdout
from tabulate import tabulate

print("\nSummary Table:")
print(tabulate(data_rows, headers=columns, tablefmt="grid"))
