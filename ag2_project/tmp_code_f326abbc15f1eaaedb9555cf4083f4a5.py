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

with open('materials_data.json') as f:
    payload = json.load(f)
    mp_results = payload.get("mp_results", [])

is_v2 = isinstance(plots_to_regenerate, list) and len(plots_to_regenerate) > 0

plots_v1_manifest = []
plots_v2_manifest = []

for plot_spec in plot_selected:
    plot_id = plot_spec["plot_id"]
    title = plot_spec["title"]
    description = plot_spec["description"]
    plot_type = plot_spec["plot_type"]
    axes = plot_spec["axes"]

    if is_v2 and plot_id not in plots_to_regenerate:
        continue

    slug = title.lower().replace(' ', '_').replace(':', '')
    if is_v2:
        out_path = os.path.join("plots_v2", f"{plot_id}_{slug}.png")
    else:
        out_path = os.path.join("plots", f"{plot_id}_{slug}.png")

    if plot_type == "scatter_2d":
        x_label = axes["x"]
        y_label = axes["y"]
        x_data = []
        y_data = []
        for entry in mp_results:
            x_value = entry.get(x_label)
            y_value = entry.get(y_label)
            if x_value is not None and y_value is not None:
                x_data.append(x_value)
                y_data.append(y_value)

        if x_data and y_data:
            plt.figure()
            plt.scatter(x_data, y_data)
            plt.xlabel(x_label.replace('_', ' ').title())
            plt.ylabel(y_label.replace('_', ' ').title())
            plt.title(title)
            plt.savefig(out_path)
            assert os.path.exists(out_path)
            plt.close()
        else:
            plt.figure()
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
            plt.savefig(out_path)
            assert os.path.exists(out_path)
            plt.close()

    elif plot_type == "histogram":
        x_label = axes["x"]
        hist_data = [entry.get(x_label) for entry in mp_results if entry.get(x_label) is not None]

        if hist_data:
            plt.figure()
            plt.hist(hist_data, bins=20, alpha=0.7)
            plt.xlabel(x_label.replace('_', ' ').title())
            plt.title(title)
            plt.savefig(out_path)
            assert os.path.exists(out_path)
            plt.close()
        else:
            plt.figure()
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
            plt.savefig(out_path)
            assert os.path.exists(out_path)
            plt.close()

    if is_v2:
        plots_v2_manifest.append({
            "plot_id": plot_id,
            "name": f"{plot_id}_{slug}.png",
            "path": out_path,
            "description": description
        })
    else:
        plots_v1_manifest.append({
            "plot_id": plot_id,
            "name": f"{plot_id}_{slug}.png",
            "path": out_path,
            "description": description
        })

summary_table_data = []

for entry in mp_results:
    material_id = entry.get("material_id")
    formula_pretty = entry.get("formula_pretty")
    band_gap = entry.get("band_gap")
    energy_above_hull = entry.get("energy_above_hull", entry.get("e_above_hull"))
    density = entry.get("density")
    if energy_above_hull is None:
        energy_above_hull = entry.get("e_above_hull")
    summary_table_data.append({
        "material_id": material_id,
        "formula_pretty": formula_pretty,
        "band_gap": band_gap,
        "energy_above_hull": energy_above_hull,
        "density": density
    })

with open("summary_table.csv", "w", newline="") as csvfile:
    fieldnames = ["material_id", "formula_pretty", "band_gap", "energy_above_hull", "density"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in summary_table_data:
        writer.writerow(data)

# Print fixed-width summary table to stdout
max_len_id = max(len(str(d["material_id"])) for d in summary_table_data)
max_len_formula = max(len(d["formula_pretty"]) for d in summary_table_data)
max_len_band_gap = max(len("Band Gap (eV)"), *(len(str(d["band_gap"])) for d in summary_table_data))
max_len_energy = max(len("Energy Above Hull (eV/atom)"), *(len(str(d["energy_above_hull"])) for d in summary_table_data))
max_len_density = max(len("Density (g/cm³)"), *(len(str(d["density"])) for d in summary_table_data))

header = f"{'Material ID':<{max_len_id}}  {'Formula':<{max_len_formula}}  {'Band Gap (eV)':<{max_len_band_gap}}  " \
         f"{'Energy Above Hull (eV/atom)':<{max_len_energy}}  {'Density (g/cm³)':<{max_len_density}}"
print(header)
print('-' * len(header))

for data in summary_table_data:
    print(f"{data['material_id']:<{max_len_id}}  {data['formula_pretty']:<{max_len_formula}}  {data['band_gap']:<{max_len_band_gap}}  "
          f"{data['energy_above_hull']:<{max_len_energy}}  {data['density']:<{max_len_density}}")

manifest_path = "plots_v2_manifest.json" if is_v2 else "plots_v1_manifest.json"
manifest_content = plots_v2_manifest if is_v2 else plots_v1_manifest

with open(manifest_path, "w") as manifest_file:
    json.dump(manifest_content, manifest_file, indent=2)
