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

# Load the materials data
with open('materials_data.json', 'r') as f:
    payload = json.load(f)
    mp_results = payload.get('mp_results', [])

# Plot 1: Band Gap vs Density Scatter Plot
try:
    densities = [material['density'] for material in mp_results if material.get('density') is not None]
    band_gaps = [material['band_gap'] for material in mp_results if material.get('band_gap') is not None]
    plt.figure()
    plt.scatter(densities, band_gaps)
    plt.title('Band Gap vs Density')
    plt.xlabel('Density (g/cm³)')
    plt.ylabel('Band Gap (eV)')
    plt.savefig('plots/P01_band_gap_vs_density_scatter_plot.png')
    plt.close()
except Exception as e:
    plt.figure()
    plt.text(0.5, 0.5, 'Plot could not be generated', fontsize=12, ha='center')
    plt.savefig('plots/P01_band_gap_vs_density_scatter_plot.png')
    plt.close()

# Plot 2: Energy Above Hull Distribution
try:
    energy_above_hull = [material['energy_above_hull'] for material in mp_results if material.get('energy_above_hull') is not None]
    plt.figure()
    plt.hist(energy_above_hull, bins=20, color='skyblue')
    plt.title('Energy Above Hull Distribution')
    plt.xlabel('Energy Above Hull (eV)')
    plt.ylabel('Frequency')
    plt.savefig('plots/P02_energy_above_hull_distribution.png')
    plt.close()
except Exception as e:
    plt.figure()
    plt.text(0.5, 0.5, 'Plot could not be generated', fontsize=12, ha='center')
    plt.savefig('plots/P02_energy_above_hull_distribution.png')
    plt.close()

# Plot 3: Band Gap Range Histogram
try:
    plt.figure()
    plt.hist(band_gaps, bins=20, color='orange')
    plt.title('Band Gap Range Histogram')
    plt.xlabel('Band Gap (eV)')
    plt.ylabel('Frequency')
    plt.savefig('plots/P03_band_gap_range_histogram.png')
    plt.close()
except Exception as e:
    plt.figure()
    plt.text(0.5, 0.5, 'Plot could not be generated', fontsize=12, ha='center')
    plt.savefig('plots/P03_band_gap_range_histogram.png')
    plt.close()

# Plot 4: Multi-dimensional Property Comparison
try:
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    energy = [material['energy_above_hull'] for material in mp_results if material.get('energy_above_hull') is not None]
    ax.scatter(densities, band_gaps, energy)
    ax.set_title('3D Property Comparison')
    ax.set_xlabel('Density (g/cm³)')
    ax.set_ylabel('Band Gap (eV)')
    ax.set_zlabel('Energy Above Hull (eV)')
    plt.savefig('plots/P05_multi_dimensional_property_comparison.png')
    plt.close()
except Exception as e:
    plt.figure()
    plt.text(0.5, 0.5, 'Plot could not be generated', fontsize=12, ha='center')
    plt.savefig('plots/P05_multi_dimensional_property_comparison.png')
    plt.close()

# Plot 5: Property Interaction Map
try:
    plt.figure(figsize=(10, 6))
    plt.hist2d(densities, band_gaps, weights=energy, bins=30, cmap='viridis')
    plt.colorbar(label='Energy Above Hull')
    plt.title('Property Interaction Map')
    plt.xlabel('Density (g/cm³)')
    plt.ylabel('Band Gap (eV)')
    plt.savefig('plots/P07_property_interaction_map.png')
    plt.close()
except Exception as e:
    plt.figure()
    plt.text(0.5, 0.5, 'Plot could not be generated', fontsize=12, ha='center')
    plt.savefig('plots/P07_property_interaction_map.png')
    plt.close()
