#!/usr/bin/env python3
import os
import json
PROJECT_FOLDER = os.environ.get('PROJECT_FOLDER', 'ag2_project')
os.makedirs(PROJECT_FOLDER, exist_ok=True)
os.chdir(PROJECT_FOLDER)

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

# Load the data
with open('materials_data.json', 'r') as f:
    payload = json.load(f)

mp_results = payload.get("mp_results", [])

# Prepare data for CSV
csv_data = []
for entry in mp_results:
    material_id = entry.get("material_id", "")
    formula_pretty = entry.get("formula_pretty", "")
    band_gap = entry.get("band_gap", "")
    energy_above_hull = entry.get("energy_above_hull", entry.get("e_above_hull", ""))
    density = entry.get("density", "")
    csv_data.append([material_id, formula_pretty, band_gap, energy_above_hull, density])

# Write to CSV
with open('summary_table.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["material_id", "formula_pretty", "band_gap", "energy_above_hull", "density"])
    writer.writerows(csv_data)

# Data for histogram
band_gaps = [entry.get("band_gap") for entry in mp_results if isinstance(entry.get("band_gap"), (int, float))]

# Plot histogram
plt.hist(band_gaps, bins=10, color='blue', edgecolor='black')
plt.title('Band Gap Distribution')
plt.xlabel('Band Gap (eV)')
plt.ylabel('Frequency')
plt.grid(axis='y', linestyle='--', linewidth=0.7)
plt.savefig('band_gap_histogram.png')
plt.close()
