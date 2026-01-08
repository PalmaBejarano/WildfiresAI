#!/usr/bin/env python3
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt

EXAMPLE_DIR = Path("examples/example_run")
INPUT_JSON = EXAMPLE_DIR / "materials_data.json"
OUTPUT_CSV = EXAMPLE_DIR / "summary_table.csv"
OUTPUT_PNG = EXAMPLE_DIR / "band_gap_histogram.png"


def main() -> None:
    if not INPUT_JSON.exists():
        raise FileNotFoundError(
            f"Missing input file: {INPUT_JSON}. "
            "Expected an example snapshot at examples/example_run/materials_data.json"
        )

    with INPUT_JSON.open("r") as f:
        materials_data = json.load(f)

    materials = materials_data.get("materials", [])
    if not isinstance(materials, list) or len(materials) == 0:
        raise ValueError("materials_data.json does not contain a non-empty 'materials' list.")

    rows = []
    for m in materials:
        kp = m.get("key_properties", {}) or {}
        rows.append(
            {
                "material_id": m.get("material_id"),
                "formula_pretty": m.get("formula_pretty"),
                "band_gap": kp.get("band_gap"),
                "energy_above_hull": kp.get("energy_above_hull"),
                "density": kp.get("density"),
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False)

    band_gaps = df["band_gap"].dropna().astype(float).tolist()
    plt.figure(figsize=(8, 6))
    plt.hist(band_gaps, bins=20)
    plt.title("Band Gap Distribution (Example Run)")
    plt.xlabel("Band Gap (eV)")
    plt.ylabel("Count")
    plt.grid(axis="y", alpha=0.75)
    plt.savefig(OUTPUT_PNG, dpi=200, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    main()
