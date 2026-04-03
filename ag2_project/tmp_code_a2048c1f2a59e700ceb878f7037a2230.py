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
from mpl_toolkits.mplot3d import Axes3D

# Load materials data
with open('materials_data.json', 'r') as f:
    payload = json.load(f)
    mp_results = payload.get('mp_results', [])

# Regenerate V2 plots
plot_selected = [
    {
      "plot_id": "plot_1",
      "title": "Energy Above Hull vs Band Gap",
      "description": "Scatter plot of energy above hull against band gap for retrieved materials.",
      "plot_type": "scatter_2d",
      "data_requirements": ["energy_above_hull", "band_gap"],
      "axes": {"type": "2d", "x": "energy_above_hull", "y": "band_gap"}
    },
    {
      "plot_id": "plot_2",
      "title": "Energy Above Hull vs Density",
      "description": "Scatter plot of energy above hull against density for the selection of materials.",
      "plot_type": "scatter_2d",
      "data_requirements": ["energy_above_hull", "density"],
      "axes": {"type": "2d", "x": "energy_above_hull", "y": "density"}
    },
    {
      "plot_id": "plot_3",
      "title": "Histogram of Band Gaps",
      "description": "Histogram showing the distribution of band gaps among the selected materials.",
      "plot_type": "histogram",
      "data_requirements": ["band_gap"],
      "axes": {"type": "hist", "x": "band_gap"}
    },
    {
      "plot_id": "plot_5",
      "title": "Density vs Band Gap",
      "description": "Scatter plot showing density values against band gap values for the materials.",
      "plot_type": "scatter_2d",
      "data_requirements": ["density", "band_gap"],
      "axes": {"type": "2d", "x": "density", "y": "band_gap"}
    },
    {
      "plot_id": "plot_7",
      "title": "3D Stability Visualization",
      "description": "3D scatter plot showing band gap, density, and stability (energy above hull) for each material.",
      "plot_type": "scatter_3d",
      "data_requirements": ["band_gap", "density", "energy_above_hull"],
      "axes": {"type": "3d", "x": "band_gap", "y": "density", "z": "energy_above_hull"}
    }
]

for plot_spec in plot_selected:
    plot_id = plot_spec["plot_id"]
    title = plot_spec["title"]
    description = plot_spec["description"]
    plot_type = plot_spec["plot_type"]
    axes = plot_spec["axes"]
    slug = title.lower().replace(" ", "_").replace(",", "")

    if plot_type == "scatter_2d":
        x_data = []
        y_data = []
        x_field = axes["x"]
        y_field = axes["y"]
        for material in mp_results:
            x_value = material.get(x_field)
            y_value = material.get(y_field)
            if x_value is not None and y_value is not None:
                x_data.append(x_value)
                y_data.append(y_value)
        if len(x_data) > 0 and len(x_data) == len(y_data):
            plt.figure()
            plt.scatter(x_data, y_data)
            plt.xlabel(x_field)
            plt.ylabel(y_field)
            plt.title(title)
            out_path = os.path.join("plots_v2", f"{plot_id}_{slug}.png")
            plt.savefig(out_path)
            plt.close()
            if not os.path.exists(out_path):
                raise RuntimeError(f"Plot {out_path} does not exist!")
    elif plot_type == "histogram":
        x_data = []
        x_field = axes["x"]
        for material in mp_results:
            x_value = material.get(x_field)
            if x_value is not None:
                x_data.append(x_value)
        if len(x_data) > 0:
            plt.figure()
            plt.hist(x_data, bins=20)
            plt.xlabel(x_field)
            plt.title(title)
            out_path = os.path.join("plots_v2", f"{plot_id}_{slug}.png")
            plt.savefig(out_path)
            plt.close()
            if not os.path.exists(out_path):
                raise RuntimeError(f"Plot {out_path} does not exist!")
    elif plot_type == "scatter_3d":
        x_data = []
        y_data = []
        z_data = []
        x_field = axes["x"]
        y_field = axes["y"]
        z_field = axes["z"]
        for material in mp_results:
            x_value = material.get(x_field)
            y_value = material.get(y_field)
            z_value = material.get(z_field)
            if x_value is not None and y_value is not None and z_value is not None:
                x_data.append(x_value)
                y_data.append(y_value)
                z_data.append(z_value)
        if len(x_data) > 0 and len(x_data) == len(y_data) == len(z_data):
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(x_data, y_data, z_data)
            ax.set_xlabel(x_field)
            ax.set_ylabel(y_field)
            ax.set_zlabel(z_field)
            ax.set_title(title)
            out_path = os.path.join("plots_v2", f"{plot_id}_{slug}.png")
            plt.savefig(out_path)
            plt.close()
            if not os.path.exists(out_path):
                raise RuntimeError(f"Plot {out_path} does not exist!")
    else:
        # Placeholder plot
        plt.figure()
        plt.text(0.5, 0.5, f"Insufficient data for {plot_id}", ha='center', va='center')
        plt.title(f"{title} - Insufficient data")
        plt.axis('off')
        out_path = os.path.join("plots_v2", f"{plot_id}_{slug}.png")
        plt.savefig(out_path)
        plt.close()
        if not os.path.exists(out_path):
            raise RuntimeError(f"Plot {out_path} does not exist!")

# Generate V2 manifest
v2_manifest = {
    "plots_v2": [
        {
            "plot_id": plot_spec["plot_id"],
            "name": f"{plot_spec["plot_id"]}_{title.lower().replace(' ', '_').replace(',', '')}.png",
            "path": os.path.join("plots_v2", f"{plot_spec["plot_id"]}_{title.lower().replace(' ', '_').replace(',', '')}.png"),
            "description": plot_spec["description"]
        }
        for plot_spec in plot_selected
    ]
}

with open('plots_v2_manifest.json', 'w') as f:
    json.dump(v2_manifest, f, indent=2)
