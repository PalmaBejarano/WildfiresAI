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
import numpy as np

# Load the materials data
with open('materials_data.json') as f:
    payload = json.load(f)
    mp_results = payload.get('mp_results', [])

# Helper function to extract data
 def extract_data(field):
    return [m.get(field, float('nan')) for m in mp_results]

# Extracting data
band_gap = extract_data('band_gap')
density = extract_data('density')
energy_above_hull = extract_data('energy_above_hull')

# Creating the correlation matrix
properties = np.array([band_gap, density, energy_above_hull])
corr_matrix = np.corrcoef(properties)

# Correlation Matrix for Material Properties
plt.figure(figsize=(8, 6))
plt.matshow(corr_matrix, cmap='coolwarm', fignum=1)
plt.title('Correlation Matrix for Material Properties', pad=50)
plt.xticks([0, 1, 2], ['Band Gap', 'Density', 'Energy Above Hull'])
plt.yticks([0, 1, 2], ['Band Gap', 'Density', 'Energy Above Hull'])
plt.colorbar()
plt.savefig('plots/P10_correlation_matrix.png')
plt.close()
