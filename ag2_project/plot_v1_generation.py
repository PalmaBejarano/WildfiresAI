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
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# Load materials data
with open('materials_data.json', 'r') as file:
    payload = json.load(file)

mp_results = payload.get("mp_results", [])

# Data preparation
material_data = []
for material in mp_results:
    material_id = material.get('material_id', '')
    formula_pretty = material.get('formula_pretty', '')
    band_gap = material.get('band_gap', np.nan)
    energy_above_hull = material.get('energy_above_hull', material.get('e_above_hull', np.nan))
    density = material.get('density', np.nan)
    
    material_data.append([material_id, formula_pretty, band_gap, energy_above_hull, density])

# Create DataFrame
columns = ['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density']
df = pd.DataFrame(material_data, columns=columns)

# Export CSV
csv_filename = "summary_table.csv"
df.to_csv(csv_filename, index=False)

# Plot 1: Band Gap vs Density Scatter Plot
fig, ax = plt.subplots()
ax.scatter(df['density'], df['band_gap'], alpha=0.7)
ax.set_title('Band Gap vs Density')
ax.set_xlabel('Density (g/cm3)')
ax.set_ylabel('Band Gap (eV)')
plt.savefig('plots/P01_band_gap_vs_density_scatter.png')
plt.close()

# Plot 2: Energy Above Hull Distribution
fig, ax = plt.subplots()
df['energy_above_hull'].hist(ax=ax, bins=20, alpha=0.7)
ax.set_title('Energy Above Hull Distribution')
ax.set_xlabel('Energy Above Hull (eV/atom)')
ax.set_ylabel('Count')
plt.savefig('plots/P02_energy_above_hull_distribution.png')
plt.close()

# Plot 4: Band Gap Histogram
fig, ax = plt.subplots()
df['band_gap'].hist(ax=ax, bins=20, alpha=0.7)
ax.set_title('Band Gap Histogram')
ax.set_xlabel('Band Gap (eV)')
ax.set_ylabel('Frequency')
plt.savefig('plots/P04_band_gap_histogram.png')
plt.close()

# Plot 6: Wide Band Gap Materials Distribution
fig, ax = plt.subplots()
ax.scatter(df['band_gap'], df['energy_above_hull'], alpha=0.7)
ax.set_title('Wide Band Gap Materials Distribution')
ax.set_xlabel('Band Gap (eV)')
ax.set_ylabel('Energy Above Hull (eV/atom)')
plt.savefig('plots/P06_wide_band_gap_distribution.png')
plt.close()

# Plot 7: 3D Plot of Band Gap, Density, and Energy Stability
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(df['density'], df['band_gap'], df['energy_above_hull'], alpha=0.7)
ax.set_title('3D Plot of Band Gap, Density, and Energy Stability')
ax.set_xlabel('Density (g/cm3)')
ax.set_ylabel('Band Gap (eV)')
ax.set_zlabel('Energy Above Hull (eV/atom)')
plt.savefig('plots/P07_3d_band_gap_density_energy_stability.png')
plt.close()

# Print the summary table to stdout
print(df.to_string(index=False, justify='right'))

# Create manifest for plots_v1
manifest_data = {
    "plots_v1": [
        {"plot_id": "P01", "name": "P01_band_gap_vs_density_scatter.png", "path": "plots/P01_band_gap_vs_density_scatter.png", "description": "Band Gap vs Density Scatter Plot"},
        {"plot_id": "P02", "name": "P02_energy_above_hull_distribution.png", "path": "plots/P02_energy_above_hull_distribution.png", "description": "Energy Above Hull Distribution"},
        {"plot_id": "P04", "name": "P04_band_gap_histogram.png", "path": "plots/P04_band_gap_histogram.png", "description": "Band Gap Histogram"},
        {"plot_id": "P06", "name": "P06_wide_band_gap_distribution.png", "path": "plots/P06_wide_band_gap_distribution.png", "description": "Wide Band Gap Materials Distribution"},
        {"plot_id": "P07", "name": "P07_3d_band_gap_density_energy_stability.png", "path": "plots/P07_3d_band_gap_density_energy_stability.png", "description": "3D Plot of Band Gap, Density, and Energy Stability"}
    ]
}

# Export manifest JSON file
with open('plots_v1_manifest.json', 'w') as manifest_file:
    json.dump(manifest_data, manifest_file, indent=4)
