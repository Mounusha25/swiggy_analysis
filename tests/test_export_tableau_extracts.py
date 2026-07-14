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
        "statistical_tests.csv",
        "forecast_validation.csv",
        "forecast_metrics.csv",
        "revenue_forecast.csv",
    }
    assert set(paths) == expected_files
    assert all(path.exists() for path in paths.values())

    orders = pd.read_csv(paths["orders_enriched.csv"])
    city_index = pd.read_csv(paths["city_expansion_index.csv"])
    health = pd.read_csv(paths["restaurant_health_score.csv"])
    cohort = pd.read_csv(paths["cohort_retention.csv"])
    statistical_tests = pd.read_csv(paths["statistical_tests.csv"])
    forecast_validation = pd.read_csv(paths["forecast_validation.csv"])
    forecast_metrics = pd.read_csv(paths["forecast_metrics.csv"])
    revenue_forecast = pd.read_csv(paths["revenue_forecast.csv"])

    assert {"Value_Segment", "Food Category", "Year-Month", "Quarter", "DayName"}.issubset(orders.columns)
    assert {"City", "Opportunity_Score", "City_Tier"}.issubset(city_index.columns)
    assert {"Restaurant Name", "Health_Score", "Health_Tier"}.issubset(health.columns)
    assert {"Cohort Month", "Cohort Size", "Month 0"}.issubset(cohort.columns)
    assert {"Test", "Metric", "P-Value", "Significant at 5%"}.issubset(statistical_tests.columns)
    assert {"Month", "Actual Revenue", "Naive Baseline", "3-Month Moving Average"}.issubset(forecast_validation.columns)
    assert {"Model", "MAPE (%)", "RMSE", "Holdout Months"}.issubset(forecast_metrics.columns)
    assert {"Month", "Forecast Revenue (INR)", "Selected Model"}.issubset(revenue_forecast.columns)
