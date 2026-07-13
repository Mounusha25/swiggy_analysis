from __future__ import annotations

import pandas as pd

from export_tableau_extracts import export_tableau_extracts
from tests.conftest import make_orders_df


def test_export_tableau_extracts_writes_expected_csvs(tmp_path) -> None:
    source_path = tmp_path / "orders.xlsx"
    output_dir = tmp_path / "tableau_extracts"
    make_orders_df().to_excel(source_path, index=False)

    paths = export_tableau_extracts(source_path=str(source_path), output_dir=str(output_dir))

    expected_files = {
        "orders_enriched.csv",
        "city_expansion_index.csv",
        "restaurant_health_score.csv",
        "rfm_summary.csv",
        "rfm_detail.csv",
        "cohort_retention.csv",
    }
    assert set(paths) == expected_files
    assert all(path.exists() for path in paths.values())

    orders = pd.read_csv(paths["orders_enriched.csv"])
    city_index = pd.read_csv(paths["city_expansion_index.csv"])
    health = pd.read_csv(paths["restaurant_health_score.csv"])
    cohort = pd.read_csv(paths["cohort_retention.csv"])

    assert {"Value_Segment", "Food Category", "Year-Month", "Quarter", "DayName"}.issubset(orders.columns)
    assert {"City", "Opportunity_Score", "City_Tier"}.issubset(city_index.columns)
    assert {"Restaurant Name", "Health_Score", "Health_Tier"}.issubset(health.columns)
    assert {"Cohort Month", "Cohort Size", "Month 0"}.issubset(cohort.columns)
