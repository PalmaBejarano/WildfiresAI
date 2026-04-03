#!/usr/bin/env python3
import os
PROJECT_FOLDER = os.environ.get('PROJECT_FOLDER', 'ag2_project')
os.makedirs(PROJECT_FOLDER, exist_ok=True)

import json
import pandas as pd
import matplotlib.pyplot as plt

# Load data from final_conclusion.json
with open('final_conclusion.json', 'r') as file:
    data = json.load(file)

# Extract relevant information
materials = data['mp_results']
summary = data['analysis_summary']

# Create dataframe for summary table
summary_df = pd.DataFrame(materials, columns=['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density'])

# Export summary table to CSV
summary_df.to_csv('summary_table.csv', index=False)

# Plot histogram for band gap distribution
plt.figure(figsize=(10, 6))
band_gaps = summary_df['band_gap']
plt.hist(band_gaps, bins=20, color='skyblue', edgecolor='black')
plt.title('Band Gap Distribution')
plt.xlabel('Band Gap (eV)')
plt.ylabel('Frequency')
plt.grid(axis='y', alpha=0.75)
plt.savefig('band_gap_histogram.png')
plt.close()
