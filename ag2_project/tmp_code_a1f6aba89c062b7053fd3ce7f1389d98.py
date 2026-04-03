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
import os
import matplotlib.pyplot as plt
import numpy as np

# Load the materials data
with open('materials_data.json', 'r') as f:
    data = json.load(f)
    mp_results = data.get('mp_results', [])

# Prepare the output directory
os.makedirs('plots', exist_ok=True)

# Plotting helper functions
def save_fig(fig, plot_id, slug):
    out_path = os.path.join('plots', f'{plot_id}_{slug}.png')
    fig.savefig(out_path)
    if not os.path.exists(out_path):
        raise RuntimeError(f"Failed to save plot: {out_path}")
    plt.close(fig)

# Extract necessary fields for plots
material_ids = [d.get('material_id') for d in mp_results]
formulas = [d.get('formula_pretty') for d in mp_results]
band_gaps = [d.get('band_gap') for d in mp_results]
energy_above_hull = [d.get('energy_above_hull', d.get('e_above_hull')) for d in mp_results]
densities = [d.get('density') for d in mp_results]

# Plot 1: Energy Above Hull vs Band Gap
fig, ax = plt.subplots()
ax.scatter(energy_above_hull, band_gaps)
ax.set_title('Energy Above Hull vs Band Gap')
ax.set_xlabel('Energy Above Hull (eV/atom)')
ax.set_ylabel('Band Gap (eV)')
save_fig(fig, 'plot_1', 'energy_above_hull_vs_band_gap')

# Plot 2: Band Gap Distribution
fig, ax = plt.subplots()
ax.hist([bg for bg in band_gaps if bg is not None], bins=20)
ax.set_title('Band Gap Distribution')
ax.set_xlabel('Band Gap (eV)')
ax.set_ylabel('Frequency')
save_fig(fig, 'plot_2', 'band_gap_distribution')

# Plot 3: Energy Above Hull Frequency
fig, ax = plt.subplots()
ax.hist([eah for eah in energy_above_hull if eah is not None], bins=20)
ax.set_title('Energy Above Hull Frequency')
ax.set_xlabel('Energy Above Hull (eV/atom)')
ax.set_ylabel('Frequency')
save_fig(fig, 'plot_3', 'energy_above_hull_frequency')

# Plot 4: Energy Above Hull vs Density
fig, ax = plt.subplots()
ax.scatter(energy_above_hull, densities)
ax.set_title('Energy Above Hull vs Density')
ax.set_xlabel('Energy Above Hull (eV/atom)')
ax.set_ylabel('Density (g/cm^3)')
save_fig(fig, 'plot_4', 'energy_above_hull_vs_density')

# Plot 5: Density vs Band Gap
fig, ax = plt.subplots()
ax.scatter(densities, band_gaps)
ax.set_title('Density vs Band Gap')
ax.set_xlabel('Density (g/cm^3)')
ax.set_ylabel('Band Gap (eV)')
save_fig(fig, 'plot_5', 'density_vs_band_gap')

# Generate a summary table to CSV
summary_cols = ['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density']
summary_data = []
for entry in mp_results:
    row = [entry.get(col, '') for col in summary_cols]
    summary_data.append(row)

summary_data.insert(0, summary_cols)  # Add header

with open('summary_table.csv', 'w', newline='') as csvfile:
    for row in summary_data:
        csvfile.write(','.join(map(str, row)) + '\n')

# Print readable summary to stdout
print("Material ID | Formula | Band Gap (eV) | Energy Above Hull (eV/atom) | Density (g/cm^3)")
for row in summary_data[1:]:  # skip header
    print(" | ".join(map(lambda x: f"{x: <15}", row)))

# Create manifest file
manifest = {'plots_v1': []}
for i, (plot_id, slug, description) in enumerate([
    ('plot_1', 'energy_above_hull_vs_band_gap', 'Scatter of Energy Above Hull vs Band Gap'),
    ('plot_2', 'band_gap_distribution', 'Histogram of Band Gap Distribution'),
    ('plot_3', 'energy_above_hull_frequency', 'Histogram of Energy Above Hull Frequency'),
    ('plot_4', 'energy_above_hull_vs_density', 'Scatter of Energy Above Hull vs Density'),
    ('plot_5', 'density_vs_band_gap', 'Scatter of Density vs Band Gap'),
]):
    manifest['plots_v1'].append({
        'plot_id': plot_id,
        'name': f'{plot_id}_{slug}.png',
        'path': f'plots/{plot_id}_{slug}.png',
        'description': description
    })

# Atomically write the manifest to avoid partial writes
manifest_tmp_path = 'plots_v1_manifest.tmp'
with open(manifest_tmp_path, 'w') as f:
    json.dump(manifest, f, indent=4)
os.replace(manifest_tmp_path, 'plots_v1_manifest.json')
