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

# Load the materials data
with open('materials_data.json', 'r') as f:
    payload = json.load(f)
    mp_results = payload.get('mp_results', [])

# Prepare the CSV summary table
header = ['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density']
data_rows = []
for material in mp_results:
    material_id = material.get('material_id', '')
    formula_pretty = material.get('formula_pretty', '')
    band_gap = material.get('band_gap', '')
    energy_above_hull = material.get('energy_above_hull', material.get('e_above_hull', ''))
    density = material.get('density', '')
    data_rows.append([material_id, formula_pretty, band_gap, energy_above_hull, density])

# Write to CSV
with open('summary_table.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(header)
    writer.writerows(data_rows)

# Extract band gap values for the histogram
band_gap_values = [material['band_gap'] for material in mp_results if isinstance(material.get('band_gap'), (int, float))]

# Plot the histogram of band gaps
plt.hist(band_gap_values, bins=20, color='blue', edgecolor='black')
plt.title('Histogram of Band Gap Distribution')
plt.xlabel('Band Gap (eV)')
plt.ylabel('Number of Materials')
plt.grid(True)
plt.savefig('band_gap_histogram.png')
plt.close()
