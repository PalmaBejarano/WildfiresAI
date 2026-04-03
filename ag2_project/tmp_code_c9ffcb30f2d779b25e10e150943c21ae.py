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
import csv

is_v2 = isinstance(plots_to_regenerate, list) and len(plots_to_regenerate) > 0

with open("materials_data.json") as f:
    payload = json.load(f)

mp_results = payload.get("mp_results", [])

# Extract data for the table
summary_data = []
for entry in mp_results:
    material_id = entry.get("material_id")
    formula_pretty = entry.get("formula_pretty")
    band_gap = entry.get("band_gap")
    energy_above_hull = entry.get("energy_above_hull", entry.get("e_above_hull"))
    density = entry.get("density")
    summary_data.append({
        "material_id": material_id,
        "formula_pretty": formula_pretty,
        "band_gap": band_gap,
        "energy_above_hull": energy_above_hull,
        "density": density
    })

# Write the summary to a CSV file
with open("summary_table.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["material_id", "formula_pretty", "band_gap", "energy_above_hull", "density"])
    writer.writeheader()
    writer.writerows(summary_data)

# Print table data
print("{:<15} {:<15} {:<10} {:<20} {:<10}".format("material_id", "formula_pretty", "band_gap", "energy_above_hull", "density"))
for data in summary_data:
    print("{:<15} {:<15} {:<10} {:<20} {:<10}".format(
        data["material_id"], data["formula_pretty"], data["band_gap"], data["energy_above_hull"], data["density"],
    ))

manifest = []
out_path_base = "plots_v2" if is_v2 else "plots"
manifest_file = "plots_v2_manifest.json" if is_v2 else "plots_v1_manifest.json"

for plot_spec in plot_selected:
    plot_id = plot_spec["plot_id"]
    title = plot_spec["title"]
    description = plot_spec["description"]
    plot_type = plot_spec["plot_type"]
    axes = plot_spec["axes"]
    slug = title.lower().replace(" ", "_").replace("/", "_")
    out_path = os.path.join(out_path_base, f"{plot_id}_{slug}.png")

    if plot_type == "scatter_2d":
        x_key = axes["x"]
        y_key = axes["y"]
        x_data = [entry[x_key] for entry in mp_results if x_key in entry]
        y_data = [entry[y_key] for entry in mp_results if y_key in entry]
        if x_data and y_data:
            plt.figure()
            plt.scatter(x_data, y_data)
            plt.xlabel(x_key.replace("_", " ").title())
            plt.ylabel(y_key.replace("_", " ").title())
            plt.title(title)
            plt.savefig(out_path)
            plt.close()
        else:
            plt.figure()
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
            plt.savefig(out_path)
            plt.close()

    elif plot_type == "histogram":
        hist_key = axes["x"]
        hist_data = [entry[hist_key] for entry in mp_results if hist_key in entry]
        if hist_data:
            plt.figure()
            plt.hist(hist_data, bins=30)
            plt.xlabel(hist_key.replace("_", " ").title())
            plt.title(title)
            plt.savefig(out_path)
            plt.close()
        else:
            plt.figure()
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
            plt.savefig(out_path)
            plt.close()

    assert os.path.exists(out_path)

    manifest.append({
        "plot_id": plot_id,
        "name": f"{plot_id}_{slug}.png",
        "path": out_path,
        "description": description
    })

with open(manifest_file, "w") as f:
    json.dump(manifest, f, indent=4)
