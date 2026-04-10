#!/usr/bin/env python3
import os
import json
PROJECT_FOLDER = os.environ.get('PROJECT_FOLDER', 'ag2_project')
os.makedirs(PROJECT_FOLDER, exist_ok=True)
os.chdir(PROJECT_FOLDER)

PATHS = {
    'data_raw': os.path.join(PROJECT_FOLDER, 'data', 'raw'),
    'data_processed': os.path.join(PROJECT_FOLDER, 'data', 'processed'),
    'plots_v1': os.path.join(PROJECT_FOLDER, 'plots', 'v1'),
    'plots_v2': os.path.join(PROJECT_FOLDER, 'plots', 'v2'),
    'plots_manifests': os.path.join(PROJECT_FOLDER, 'plots', 'manifests'),
    'reports_latex': os.path.join(PROJECT_FOLDER, 'reports', 'latex'),
    'reports_pdf': os.path.join(PROJECT_FOLDER, 'reports', 'pdf'),
    'scripts': os.path.join(PROJECT_FOLDER, 'scripts', 'generated'),
    'tmp': os.path.join(PROJECT_FOLDER, 'tmp'),
}
for _path in PATHS.values():
    os.makedirs(_path, exist_ok=True)

PLOTS_DIR_V1 = PATHS['plots_v1']
PLOTS_DIR_V2 = PATHS['plots_v2']

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
    materials_path = os.path.join(PATHS['data_processed'], 'materials_data.json')
    cwd_materials_path = os.path.join(PROJECT_FOLDER, 'materials_data.json')
    final_conclusion_path = os.path.join(PATHS['data_processed'], 'final_conclusion.json')
    if os.path.exists(materials_path):
        try:
            with open(materials_path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
            with open(cwd_materials_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
        except Exception:
            pass
        return
    if not os.path.exists(final_conclusion_path):
        return
    try:
        with open(final_conclusion_path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    except Exception:
        return
    mp_results = payload.get('mp_results')
    analysis_summary = payload.get('analysis_summary')
    final_conclusion = payload.get('final_conclusion')
    if mp_results is None:
        return
    materials_payload = {
        'mp_results': mp_results,
        'analysis_summary': analysis_summary,
        'final_conclusion': final_conclusion,
    }
    with open(materials_path, 'w', encoding='utf-8') as f:
        json.dump(materials_payload, f, indent=2, ensure_ascii=False, default=str)
    with open(cwd_materials_path, 'w', encoding='utf-8') as f:
        json.dump(materials_payload, f, indent=2, ensure_ascii=False, default=str)

_ensure_materials_data_json()

import json
import os
import matplotlib.pyplot as plt

with open("materials_data.json", "r") as f:
    payload = json.load(f)
    mp_results = payload.get("mp_results", [])

summary_data = []
for material in mp_results:
    material_id = material.get("material_id")
    formula_pretty = material.get("formula_pretty")
    band_gap = material.get("band_gap")
    energy_above_hull = material.get("energy_above_hull", material.get("e_above_hull"))
    density = material.get("density")
    summary_data.append([material_id, formula_pretty, band_gap, energy_above_hull, density])

summary_table_path = os.path.join(PATHS["data_processed"], "summary_table.csv")
with open(summary_table_path, "w") as f:
    f.write("material_id,formula_pretty,band_gap,energy_above_hull,density\n")
    for row in summary_data:
        f.write(",".join(map(str, row)) + "\n")

try:
    plots_to_regenerate
except NameError:
    plots_to_regenerate = None

is_v2 = isinstance(plots_to_regenerate, list) and len(plots_to_regenerate) > 0

label_map = {
    "band_gap": "Band Gap (eV)",
    "density": "Density (g/cm³)",
    "energy_above_hull": "Energy Above Hull (eV/atom)",
    "e_above_hull": "Energy Above Hull (eV/atom)",
}

manifest = []

for plot_spec in plot_selected:
    plot_id = plot_spec["plot_id"]
    title = plot_spec["title"]
    description = plot_spec["description"]
    plot_type = plot_spec["plot_type"]
    axes = plot_spec["axes"]
    slug = plot_type
    out_path = os.path.join(PATHS["plots_v2"] if is_v2 else PATHS["plots_v1"], f"{plot_id}_{slug}.png")

    if is_v2 and plot_id not in plots_to_regenerate:
        continue

    if plot_type == "scatter_2d":
        x_data, y_data = [], []
        for material in mp_results:
            x_val = material.get(axes["x"])
            y_val = material.get(axes["y"])
            if x_val is None or y_val is None:
                continue
            x_data.append(x_val)
            y_data.append(y_val)
        if not x_data or not y_data:
            plt.figure()
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
            plt.savefig(out_path)
            assert os.path.exists(out_path)
            plt.close()
        else:
            plt.figure()
            plt.scatter(x_data, y_data)
            plt.xlabel(label_map.get(axes["x"], axes["x"]))
            plt.ylabel(label_map.get(axes["y"], axes["y"]))
            plt.title(title)
            plt.savefig(out_path)
            assert os.path.exists(out_path)
            plt.close()
    elif plot_type == "histogram":
        hist_data = []
        for material in mp_results:
            x_val = material.get(axes["x"])
            if x_val is None:
                continue
            hist_data.append(x_val)
        if not hist_data:
            plt.figure()
            plt.title(f"{plot_id} - Insufficient data")
            plt.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
            plt.savefig(out_path)
            assert os.path.exists(out_path)
            plt.close()
        else:
            plt.figure()
            plt.hist(hist_data, bins=30)
            plt.xlabel(label_map.get(axes["x"], axes["x"]))
            plt.ylabel("Frequency")
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

    name = f"{plot_id}_{slug}.png"
    manifest_entry = {
        "plot_id": plot_id,
        "name": name,
        "path": out_path,
        "description": description,
    }
    manifest.append(manifest_entry)

manifest_path = os.path.join(PATHS["plots_manifests"], "plots_v2_manifest.json" if is_v2 else "plots_v1_manifest.json")
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)
