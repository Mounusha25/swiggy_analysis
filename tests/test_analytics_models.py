from __future__ import annotations

import pandas as pd
import pytest

from analytics_models import (
    calculate_cohort_retention,
    calculate_rfm_segments,
    calculate_restaurant_frequency_tiers,
    classify_food_category,
    prepare_order_data,
)
from tests.conftest import make_orders_df


@pytest.mark.parametrize(
    ("dish_name", "expected"),
    [
        ("Veg Biryani", "Veg"),
        ("Chicken Biryani", "Non-Veg"),
        ("Paneer Kebab", "Veg"),
        ("Chicken Kebab", "Non-Veg"),
        ("Eggless Chocolate Cake", "Veg"),
        ("Egg Curry", "Non-Veg"),
        ("Non-Veg Meal Combo", "Non-Veg"),
        ("Mushroom Pizza", "Veg"),
    ],
)
def test_classify_food_category_handles_edge_cases(dish_name: str, expected: str) -> None:
    result = classify_food_category(pd.Series([dish_name]))

    assert result.iloc[0] == expected


def test_prepare_order_data_adds_expected_derived_columns() -> None:
    prepared = prepare_order_data(make_orders_df(), include_synthetic_hour=True)

    first_row = prepared.iloc[0]
    premium_row = prepared.loc[prepared["Dish Name"] == "Paneer Pizza"].iloc[0]

    assert first_row["Year-Month"] == "2025-01"
    assert first_row["Quarter"] == "2025Q1"
    assert first_row["DayName"] == "Sunday"
    assert first_row["DayOfWeek"] == 6
    assert str(first_row["Value_Segment"]) == "Budget (<=200)"
    assert str(premium_row["Value_Segment"]) == "Premium (501-1000)"
    assert prepared.loc[prepared["Dish Name"] == "Veg Biryani", "Food Category"].iloc[0] == "Veg"
    assert prepared.loc[prepared["Dish Name"] == "Chicken Biryani", "Food Category"].iloc[0] == "Non-Veg"
    assert prepared["Order Hour"].between(0, 23).all()
    assert prepared["Time Slot"].notna().all()


def test_calculate_rfm_segments_returns_expected_partner_metrics() -> None:
    rfm, summary = calculate_rfm_segments(make_orders_df())

    alpha = rfm.loc[rfm["Restaurant Name"] == "Alpha"].iloc[0]

    assert len(rfm) == 3
    assert set(rfm["Restaurant Name"]) == {"Alpha", "Beta", "Gamma"}
    assert alpha["Frequency"] == 3
    assert alpha["Monetary"] == 1400
    assert {"RFM_Score", "RFM_Code", "RFM_Segment"}.issubset(rfm.columns)
    assert summary["Entities"].sum() == 3


def test_calculate_restaurant_frequency_tiers_uses_shared_40_80_split() -> None:
    tiers = calculate_restaurant_frequency_tiers(make_orders_df())
    by_restaurant = tiers.set_index("Restaurant Name")

    assert len(tiers) == 3
    assert by_restaurant.loc["Alpha", "Orders"] == 3
    assert by_restaurant.loc["Alpha", "Frequency Tier"] == "High Volume (Top 20%)"
    assert by_restaurant.loc["Beta", "Frequency Tier"] == "Low Volume (Bottom 40%)"
    assert by_restaurant.loc["Gamma", "Frequency Tier"] == "Medium Volume (40-80%)"


def test_calculate_cohort_retention_builds_monthly_matrix() -> None:
    cohort = calculate_cohort_retention(make_orders_df())

    jan_cohort = cohort.loc[cohort["Cohort Month"] == "2025-01"].iloc[0]
    feb_cohort = cohort.loc[cohort["Cohort Month"] == "2025-02"].iloc[0]

    assert list(cohort["Cohort Month"]) == ["2025-01", "2025-02"]
    assert jan_cohort["Cohort Size"] == 1
    assert jan_cohort["Month 0"] == 100.0
    assert jan_cohort["Month 2"] == 100.0
    assert feb_cohort["Cohort Size"] == 2
    assert feb_cohort["Month 1"] == 50.0
