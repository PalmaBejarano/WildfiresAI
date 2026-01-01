#!/usr/bin/env python3
import os
PROJECT_FOLDER = os.environ.get('PROJECT_FOLDER', 'ag2_project')
os.makedirs(PROJECT_FOLDER, exist_ok=True)
os.chdir(PROJECT_FOLDER)

import pandas as pd
import json

# Loading data
with open('ag2_project/materials_data.json', 'r') as file:
    materials_data = json.load(file)

# Extracting required fields for CSV
summary_data = []
for material in materials_data['materials']:
    entry = {
        "material_id": material['material_id'],
        "formula_pretty": material['formula_pretty'],
        "band_gap": material['key_properties']['band_gap'],
        "energy_above_hull": material['key_properties']['energy_above_hull'],
    }
    summary_data.append(entry)

# Creating a DataFrame and exporting to CSV
summary_df = pd.DataFrame(summary_data)
summary_df.to_csv('ag2_project/summary_table.csv', index=False)