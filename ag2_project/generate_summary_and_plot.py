#!/usr/bin/env python3
import os
PROJECT_FOLDER = os.environ.get('PROJECT_FOLDER', 'ag2_project')
os.makedirs(PROJECT_FOLDER, exist_ok=True)
os.chdir(PROJECT_FOLDER)

import json
import pandas as pd
import matplotlib.pyplot as plt

# Load the materials data
with open('materials_data.json', 'r') as file:
    materials_data = json.load(file)

# Extract relevant fields for the summary table
summary_data = [
    {
        "material_id": m["material_id"],
        "formula_pretty": m["formula_pretty"],
        "band_gap": m["key_properties"]["band_gap"],
        "energy_above_hull": m["key_properties"]["energy_above_hull"],
        "density": m["key_properties"]["density"]
    }
    for m in materials_data["materials"]
]

# Create a DataFrame
summary_df = pd.DataFrame(summary_data)

# Export the summary to a CSV file
summary_df.to_csv('summary_table.csv', index=False)

# Plot the histogram of band_gap distribution
plt.figure(figsize=(10, 6))
plt.hist(summary_df['band_gap'], bins=10, color='skyblue', edgecolor='black')
plt.title('Histogram of Band Gap Distribution')
plt.xlabel('Band Gap (eV)')
plt.ylabel('Frequency')
plt.grid(axis='y', alpha=0.75)
plt.savefig('band_gap_histogram.png')
plt.close()