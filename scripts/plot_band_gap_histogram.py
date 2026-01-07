#!/usr/bin/env python3
import os
PROJECT_FOLDER = os.environ.get('PROJECT_FOLDER', 'ag2_project')
os.makedirs(PROJECT_FOLDER, exist_ok=True)
os.chdir(PROJECT_FOLDER)

import matplotlib.pyplot as plt
import json

# Load the data
with open('ag2_project/materials_data.json', 'r') as file:
    materials_data = json.load(file)

# Extract band gaps
band_gaps = [material['key_properties']['band_gap'] for material in materials_data['materials'] if material['key_properties']['band_gap'] is not None]

# Plotting
plt.figure(figsize=(8, 6))
plt.hist(band_gaps, bins=30, color='skyblue', edgecolor='black')
plt.title('Distribution of Band Gaps for Selected Materials')
plt.xlabel('Band Gap (eV)')
plt.ylabel('Frequency')
plt.grid(axis='y', alpha=0.75)
plt.savefig('ag2_project/band_gap_histogram.png')
plt.close()