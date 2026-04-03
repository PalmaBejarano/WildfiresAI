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
import matplotlib.pyplot as plt
import csv
from os import makedirs
from os.path import exists

# Ensure the plots directory exists
makedirs('plots', exist_ok=True)

# Load materials data
with open('materials_data.json') as f:
    payload = json.load(f)
    mp_results = payload.get("mp_results", [])

# CSV Export
csv_columns = ['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density']
with open('summary_table.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for entry in mp_results:
        writer.writerow({field: entry.get(field, '') for field in csv_columns})

# Table Print to stdout
print("{:<12} {:<15} {:<8} {:<17} {:<7}".format('material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density'))
for entry in mp_results:
    print("{:<12} {:<15} {:<8} {:<17} {:<7}".format(
        entry.get('material_id', ''),
        entry.get('formula_pretty', ''),
        entry.get('band_gap', ''),
        entry.get('energy_above_hull', ''),
        entry.get('density', '')
    ))

# Helper to save placeholder
placeholder_text = "Data Not Available"
def save_placeholder(plot_id, slug):
    plt.figure(figsize=(6, 4))
    plt.text(0.5, 0.5, placeholder_text, fontsize=12, ha='center')
    plt.axis('off')
    plt.savefig(f"plots/{plot_id}_{slug}.png")
    plt.close()

if not mp_results:
    for plot in plot_selected:
        save_placeholder(plot["plot_id"], plot["title"].replace(' ', '_').lower())
else:
    # Generate and save plots
    # Plot P01: Energy Above Hull Distribution
    try:
        plt.figure(figsize=(12, 6))
        plt.bar(range(len(mp_results)), 
                [entry.get('energy_above_hull', 0) for entry in mp_results],
                color='skyblue')
        plt.xlabel('Material ID')
        plt.ylabel('Energy Above Hull')
        plt.title('Energy Above Hull Distribution')
        plt.savefig('plots/P01_energy_above_hull_distribution.png')
        plt.close()
    except Exception as e:
        save_placeholder('P01', 'energy_above_hull_distribution')

    # Plot P02: Band Gap vs Density
    try:
        plt.figure(figsize=(12, 6))
        plt.scatter(
            [entry.get('band_gap', 0) for entry in mp_results],
            [entry.get('density', 0) for entry in mp_results],
            c='blue', marker='o'
        )
        plt.xlabel('Band Gap (eV)')
        plt.ylabel('Density (g/cm^3)')
        plt.title('Band Gap vs Density')
        plt.savefig('plots/P02_band_gap_vs_density.png')
        plt.close()
    except Exception as e:
        save_placeholder('P02', 'band_gap_vs_density')

    # Plot P05: Stability Classes
    try:
        stability_classes = {'Stable (0 eV)': 0, 'Near-Stable (<=0.05 eV)': 0}
        for entry in mp_results:
            energy_above_hull = entry.get('energy_above_hull', 0)
            if energy_above_hull == 0:
                stability_classes['Stable (0 eV)'] += 1
            elif 0 < energy_above_hull <= 0.05:
                stability_classes['Near-Stable (<=0.05 eV)'] += 1
        
        plt.figure(figsize=(10, 6))
        plt.bar(stability_classes.keys(), stability_classes.values(), color=['green', 'orange'])
        plt.xlabel('Stability Class')
        plt.ylabel('Count')
        plt.title('Stability Classes')
        plt.savefig('plots/P05_stability_classes.png')
        plt.close()
    except Exception as e:
        save_placeholder('P05', 'stability_classes')

    # Plot P08: Energy Efficiency vs Insulation Plot
    try:
        plt.figure(figsize=(10, 6))
        plt.scatter(
            [entry.get('band_gap', 0) for entry in mp_results],
            [entry.get('energy_above_hull', 0) for entry in mp_results],
            c='purple', alpha=0.5
        )
        plt.xlabel('Band Gap (eV)')
        plt.ylabel('Energy Above Hull (eV)')
        plt.title('Energy Efficiency vs Insulation Plot')
        plt.savefig('plots/P08_energy_efficiency_vs_insulation.png')
        plt.close()
    except Exception as e:
        save_placeholder('P08', 'energy_efficiency_vs_insulation')

    # Plot P09: Extracted Information Multivariate Chart
    try:
        plt.figure(figsize=(12, 6))
        sc = plt.scatter(
            range(len(mp_results)), [entry.get('band_gap', 0) for entry in mp_results], 
            s=[entry.get('density', 1)*10 for entry in mp_results], 
            c=[entry.get('energy_above_hull', 0) for entry in mp_results], cmap='viridis', alpha=0.6
        )
        plt.colorbar(sc, label='Energy Above Hull (eV)')
        plt.xlabel('Material ID')
        plt.ylabel('Band Gap (eV)')
        plt.title('Extracted Information Multivariate Chart')
        plt.savefig('plots/P09_extracted_information_multivariate_chart.png')
        plt.close()
    except Exception as e:
        save_placeholder('P09', 'extracted_information_multivariate_chart')

# Create manifest
plot_manifest = [
    {"plot_id": "P01", "name": "P01_energy_above_hull_distribution.png", "path": "plots/P01_energy_above_hull_distribution.png", "description": "Energy Above Hull Distribution"},
    {"plot_id": "P02", "name": "P02_band_gap_vs_density.png", "path": "plots/P02_band_gap_vs_density.png", "description": "Band Gap vs Density"},
    {"plot_id": "P05", "name": "P05_stability_classes.png", "path": "plots/P05_stability_classes.png", "description": "Stability Classes"},
    {"plot_id": "P08", "name": "P08_energy_efficiency_vs_insulation.png", "path": "plots/P08_energy_efficiency_vs_insulation.png", "description": "Energy Efficiency vs Insulation Plot"},
    {"plot_id": "P09", "name": "P09_extracted_information_multivariate_chart.png", "path": "plots/P09_extracted_information_multivariate_chart.png", "description": "Extracted Information Multivariate Chart"}
]

with open('plots_v1_manifest.json', 'w') as f:
    json.dump({"plots_v1": plot_manifest}, f)
