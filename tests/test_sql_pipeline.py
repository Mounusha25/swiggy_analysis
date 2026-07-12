from __future__ import annotations

import pandas as pd
import pytest

from sql_pipeline import QUERIES, run_query, setup_database
from tests.conftest import make_orders_df


@pytest.fixture()
def fixture_db(tmp_path):
    db_path = tmp_path / "swiggy_test.db"
    setup_database(db_path=str(db_path), source_df=make_orders_df())
    return str(db_path)


@pytest.mark.parametrize("query_name", list(QUERIES.keys()))
def test_all_sql_queries_run_against_fixture_db(fixture_db: str, query_name: str) -> None:
    result = run_query(QUERIES[query_name]["sql"], fixture_db)

    assert isinstance(result, pd.DataFrame)
    assert not result.empty


def test_monthly_revenue_query_returns_expected_values(fixture_db: str) -> None:
    result = run_query(QUERIES["Monthly Revenue & Seasonality"]["sql"], fixture_db)

    jan = result.loc[result["Month"] == "2025-01"].iloc[0]
    mar = result.loc[result["Month"] == "2025-03"].iloc[0]

    assert len(result) == 3
    assert jan["Orders"] == 2
    assert jan["Revenue (INR)"] == 500
    assert mar["Orders"] == 2
    assert mar["Revenue (INR)"] == 2100


def test_customer_basket_segmentation_query_returns_expected_segments(fixture_db: str) -> None:
    result = run_query(QUERIES["Customer Basket Segmentation"]["sql"], fixture_db)
    by_segment = result.set_index("Segment")

    assert by_segment.loc["Budget (<=200)", "Orders"] == 1
    assert by_segment.loc["Standard (201-500)", "Orders"] == 2
    assert by_segment.loc["Premium (501-1000)", "Orders"] == 2
    assert by_segment.loc["Luxury (>1000)", "Orders"] == 1


def test_restaurant_cohort_retention_query_returns_expected_values(fixture_db: str) -> None:
    result = run_query(QUERIES["Restaurant Cohort Retention"]["sql"], fixture_db)

    jan_month_2 = result[
        (result["Cohort_Month"] == "2025-01")
        & (result["Months Since First Order"] == 2)
    ].iloc[0]
    feb_month_1 = result[
        (result["Cohort_Month"] == "2025-02")
        & (result["Months Since First Order"] == 1)
    ].iloc[0]

    assert jan_month_2["Retention %"] == 100.0
    assert feb_month_1["Retention %"] == 50.0


def test_restaurant_rfm_query_includes_expected_top_partner(fixture_db: str) -> None:
    result = run_query(QUERIES["Restaurant RFM Segmentation"]["sql"], fixture_db)

    alpha = result.loc[result["Restaurant"] == "Alpha"].iloc[0]

    assert alpha["Frequency"] == 3
    assert alpha["Revenue (INR)"] == 1400
    assert alpha["RFM_Segment"] in {
        "Champions",
        "Loyal Partners",
        "Big Spenders",
        "At Risk",
        "Hibernating",
        "Emerging",
    }
