#!/usr/bin/env python3
import os
PROJECT_FOLDER = os.environ.get('PROJECT_FOLDER', 'ag2_project')
os.makedirs(PROJECT_FOLDER, exist_ok=True)

import pandas as pd
import json
import matplotlib.pyplot as plt

# Load data from JSON file
with open("materials_data.json", "r") as file:
    data = json.load(file)

# Create a dataframe for the selected fields
materials_df = pd.DataFrame(data['summary'])

# Drop rows where any of the specified columns have missing data
materials_df = materials_df.dropna(subset=['material_id', 'formula_pretty', 'band_gap', 'energy_above_hull', 'density'])

# Save to a CSV file
materials_df.to_csv('summary_table.csv', index=False)

# Plot histogram of band_gap
plt.hist(materials_df['band_gap'], bins=10, color='skyblue', edgecolor='black')
plt.xlabel('Band Gap (eV)')
plt.ylabel('Frequency')
plt.title('Histogram of Band Gap Distribution')
plt.savefig('band_gap_histogram.png')
plt.close()