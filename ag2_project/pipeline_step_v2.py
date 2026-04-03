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

with open('materials_data.json') as f:
    payload = json.load(f)
    mp_results = payload.get("mp_results", [])

plots_v2_manifest = []

for plot_spec in plot_selected:
    plot_id = plot_spec["plot_id"]
    title = plot_spec["title"]
    description = plot_spec["description"]
    plot_type = plot_spec["plot_type"]
    axes = plot_spec["axes"]

    if plot_id not in plots_to_regenerate:
        continue

    slug = title.lower().replace(' ', '_').replace(':', '')
    out_path = os.path.join("plots_v2", f"{plot_id}_{slug}.png")

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

        plt.figure()
        if x_data and y_data:
            plt.scatter(x_data, y_data, alpha=0.5)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.xlabel(x_label.replace('energy_above_hull','Energy Above Hull (eV/atom)').replace('density','Density (g/cm³)').replace('_', ' ').title())
            plt.ylabel(y_label.replace('band_gap','Band Gap (eV)').replace('density','Density (g/cm³)').replace('_', ' ').title())
        else:
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")

        plt.title(title)
        plt.savefig(out_path)
        assert os.path.exists(out_path)
        plt.close()

    elif plot_type == "histogram":
        x_label = axes["x"]
        hist_data = [entry.get(x_label) for entry in mp_results if entry.get(x_label) is not None]

        plt.figure()
        if hist_data:
            plt.hist(hist_data, bins=20, alpha=0.7)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.xlabel(x_label.replace('density','Density (g/cm³)').replace('band_gap','Band Gap (eV)').replace('_', ' ').title())
            plt.ylabel('Frequency')
        else:
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")

        plt.title(title)
        plt.savefig(out_path)
        assert os.path.exists(out_path)
        plt.close()

    plots_v2_manifest.append({
        "plot_id": plot_id,
        "name": f"{plot_id}_{slug}.png",
        "path": out_path,
        "description": description
    })

with open("plots_v2_manifest.json", "w") as manifest_file:
    json.dump(plots_v2_manifest, manifest_file, indent=2)
