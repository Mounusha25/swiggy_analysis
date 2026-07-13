"""
Export Tableau-ready CSV extracts from the shared analytics layer.

Tableau should consume flat, business-ready extracts rather than reimplementing
Python scoring logic in calculated fields.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from analytics_models import (
    calculate_city_expansion_index,
    calculate_cohort_retention,
    calculate_restaurant_health_score,
    calculate_rfm_segments,
    prepare_order_data,
)


DEFAULT_EXCEL_PATH = "swiggy_data.xlsx"
DEFAULT_OUTPUT_DIR = "tableau_extracts"


def export_tableau_extracts(
    source_path: str = DEFAULT_EXCEL_PATH,
    output_dir: str = DEFAULT_OUTPUT_DIR,
) -> dict[str, Path]:
    """Write Tableau-ready CSV extracts and return their output paths."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    raw_df = pd.read_excel(source_path)
    orders_enriched = prepare_order_data(raw_df)
    city_expansion = calculate_city_expansion_index(raw_df)
    restaurant_health = calculate_restaurant_health_score(raw_df)
    rfm_detail, rfm_summary = calculate_rfm_segments(raw_df)
    cohort_retention = calculate_cohort_retention(raw_df)

    extracts = {
        "orders_enriched.csv": orders_enriched,
        "city_expansion_index.csv": city_expansion,
        "restaurant_health_score.csv": restaurant_health,
        "rfm_summary.csv": rfm_summary,
        "rfm_detail.csv": rfm_detail,
        "cohort_retention.csv": cohort_retention,
    }

    written_paths: dict[str, Path] = {}
    for filename, extract_df in extracts.items():
        path = output_path / filename
        extract_df.to_csv(path, index=False)
        written_paths[filename] = path

    return written_paths


if __name__ == "__main__":
    paths = export_tableau_extracts()
    print("Exported Tableau extracts:")
    for name, path in paths.items():
        print(f"- {name}: {path}")
