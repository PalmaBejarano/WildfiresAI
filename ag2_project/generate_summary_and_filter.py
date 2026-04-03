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
with open('materials_data.json', 'r') as f:
    payload = json.load(f)
    mp_results = payload.get("mp_results", [])

# Filter the materials based on the given criteria
filtered_materials = []
for material in mp_results:
    material_id = material.get("material_id", "")
    formula_pretty = material.get("formula_pretty", "")
    band_gap = material.get("band_gap", None)
    energy_above_hull = material.get("energy_above_hull", material.get("e_above_hull", None))
    density = material.get("density", None)
    elements = material.get("elements", [])

    # Check for exclusion elements
    if any(elem in ["Pb", "Cd", "Hg"] for elem in elements):
        continue

    # Apply filters
    if (band_gap is not None and 3.0 <= band_gap <= 20.0 and
        energy_above_hull is not None and 0.0 <= energy_above_hull <= 0.05 and
        density is not None and 3.0 <= density <= 10.0):
        filtered_materials.append({
            "material_id": material_id,
            "formula_pretty": formula_pretty,
            "band_gap": band_gap,
            "energy_above_hull": energy_above_hull,
            "density": density
        })

# Write summary table as CSV
with open('summary_table.csv', 'w', newline='') as csvfile:
    fieldnames = ["material_id", "formula_pretty", "band_gap", "energy_above_hull", "density"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for material in filtered_materials:
        writer.writerow(material)

# Print the table to stdout in a formatted way
row_format = "{:<12} {:<20} {:<10} {:<17} {:<8}"
print(row_format.format("Material ID", "Formula", "Band Gap", "Energy Above Hull", "Density"))
print("="*65)
for material in filtered_materials:
    print(row_format.format(material["material_id"], material["formula_pretty"], f"{material['band_gap']:.2f}", 
                            f"{material['energy_above_hull']:.2f}", f"{material['density']:.2f}"))
