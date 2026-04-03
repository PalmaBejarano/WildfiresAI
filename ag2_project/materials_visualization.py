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
import pandas as pd
import matplotlib.pyplot as plt

# Load materials data
with open("materials_data.json", "r") as file:
    payload = json.load(file)

mp_results = payload.get("mp_results", [])

# Prepare data for the table and plots
materials_data = []
band_gaps = []
density_vs_band_gap = []

# Iterate through the materials for data extraction
for material in mp_results:
    material_id = material.get("material_id", "")
    formula_pretty = material.get("formula_pretty", "")
    band_gap = material.get("band_gap", None)
    energy_above_hull = material.get("energy_above_hull", material.get("e_above_hull", None))
    density = material.get("density", None)

    # Append the material data into the list
    materials_data.append({
        "material_id": material_id,
        "formula_pretty": formula_pretty,
        "band_gap": band_gap,
        "energy_above_hull": energy_above_hull,
        "density": density
    })

    # For band gap histogram
    if isinstance(band_gap, (int, float)):
        band_gaps.append(band_gap)
    
    # For density vs band_gap scatter plot
    if isinstance(band_gap, (int, float)) and isinstance(density, (int, float)):
        density_vs_band_gap.append((density, band_gap, material_id))

# Export the data to a CSV file
summary_table = pd.DataFrame(materials_data)
summary_table.to_csv("summary_table.csv", index=False)

# Print a formatted table to stdout
print("| material_id | formula_pretty | band_gap | energy_above_hull | density |")
print("|-------------|----------------|----------|-------------------|---------|")
for data in materials_data:
    print(f"| {data['material_id']:<11} | {data['formula_pretty']:<14} | {data['band_gap']:<8} | {data['energy_above_hull']:<17} | {data['density']:<7} |")

# Generate a histogram of the band_gap distribution
plt.figure(figsize=(10, 6))
plt.hist(band_gaps, bins=20, color='blue', edgecolor='black')
plt.title('Band Gap Distribution')
plt.xlabel('Band Gap (eV)')
plt.ylabel('Number of Materials')
plt.savefig('band_gap_histogram.png')
plt.close()

# Generate a scatter plot of density vs band_gap
plt.figure(figsize=(10, 6))
density, band_gap, labels = zip(*density_vs_band_gap)
plt.scatter(density, band_gap, c='green', label='Materials')
for label, x, y in zip(labels, density, band_gap):
    plt.annotate(label, (x, y), fontsize=8, alpha=0.75)
plt.title('Density vs Band Gap')
plt.xlabel('Density (g/cm³)')
plt.ylabel('Band Gap (eV)')
plt.grid(True)
plt.savefig('materials_scatter.png')
plt.close()
