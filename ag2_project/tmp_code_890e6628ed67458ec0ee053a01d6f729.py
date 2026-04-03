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
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load the materials data
data_file = 'materials_data.json'
with open(data_file, 'r') as file:
    payload = json.load(file)

mp_results = payload.get('mp_results', [])

# Step 2: Prepare the data for CSV export
summary_data = [
    {
        'material_id': mat.get('material_id'),
        'formula_pretty': mat.get('formula_pretty'),
        'band_gap': mat.get('band_gap'),
        'energy_above_hull': mat.get('energy_above_hull') or mat.get('e_above_hull'),
        'density': mat.get('density')
    }
    for mat in mp_results
]

# Convert to DataFrame
summary_df = pd.DataFrame(summary_data)

# Export the summary table to CSV
summary_df.to_csv('summary_table.csv', index=False)

# Print compact table
print(summary_df)

# Step 3: Generate the plots
# Plot 1: Energy vs Band Gap
plt.figure(figsize=(10, 6))
plt.scatter(summary_df['energy_above_hull'], summary_df['band_gap'], c='blue', alpha=0.5)
plt.xlabel('Energy Above Hull (eV/atom)')
plt.ylabel('Band Gap (eV)')
plt.title('Energy vs Band Gap')
plt.grid(True)
plt.savefig('plots/P01_energy_vs_band_gap.png')
plt.close()

# Plot 2: Energy vs Density
plt.figure(figsize=(10, 6))
plt.scatter(summary_df['energy_above_hull'], summary_df['density'], c='green', alpha=0.5)
plt.xlabel('Energy Above Hull (eV/atom)')
plt.ylabel('Density (g/cm³)')
plt.title('Energy vs Density')
plt.grid(True)
plt.savefig('plots/P03_energy_vs_density.png')
plt.close()

# Plot 3: Material Stability Categories
stability_bins = [-0.01, 0.01, 0.05]
stability_labels = ['Stable', 'Near-Stable']
summary_df['stability_category'] = pd.cut(summary_df['energy_above_hull'], bins=stability_bins, labels=stability_labels)
stability_counts = summary_df['stability_category'].value_counts()

plt.figure(figsize=(8, 6))
stability_counts.plot(kind='bar', color='orange')
plt.xlabel('Stability Category')
plt.ylabel('Count')
plt.title('Material Stability Categories')
plt.grid(True)
plt.savefig('plots/P05_material_stability_categories.png')
plt.close()

# Plot 4: Average Properties Summary
plt.figure(figsize=(10, 6))
sns.boxplot(data=summary_df[['band_gap', 'energy_above_hull', 'density']])
plt.title('Average Properties Summary')
plt.ylabel('Value')
plt.grid(True)
plt.savefig('plots/P07_average_properties_summary.png')
plt.close()

# Plot 5: Correlation Matrix of Properties
plt.figure(figsize=(8, 6))
corr_matrix = summary_df[['band_gap', 'energy_above_hull', 'density']].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Matrix of Properties')
plt.savefig('plots/P09_correlation_matrix_of_properties.png')
plt.close()

# Step 4: Write the manifest
def write_manifest(manifest_path, plots):
    manifest_dict = {
        "plots_v1": [
            {
                "plot_id": plot['plot_id'],
                "name": f"{plot['plot_id']}_{plot['title'].replace(' ', '_').lower()}.png",
                "path": f"plots/{plot['plot_id']}_{plot['title'].replace(' ', '_').lower()}.png",
                "description": plot['description']
            }
            for plot in plots
        ]
    }
    with open(manifest_path, 'w') as f:
        json.dump(manifest_dict, f, indent=4)

write_manifest('plots_v1_manifest.json', [
    {"plot_id": "P01", "title": "Energy vs Band Gap", "description": "Scatter plot showing the relationship between energy_above_hull and band_gap for the materials. This helps visualize stability versus insulating capability."},
    {"plot_id": "P03", "title": "Energy vs Density", "description": "Scatter plot illustrating energy_above_hull against density. This highlights any potential trade-offs between stability and material weight or structure."},
    {"plot_id": "P05", "title": "Material Stability Categories", "description": "Bar chart depicting the counts of materials classified by stability category based on energy_above_hull intervals."},
    {"plot_id": "P07", "title": "Average Properties Summary", "description": "Box plot showing the spread and average values for band-gap, density, and energy_above_hull across materials."},
    {"plot_id": "P09", "title": "Correlation Matrix of Properties", "description": "Heat map illustrating the correlations between band_gap, energy_above_hull, and density."}
])
