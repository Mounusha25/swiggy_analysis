"""
Reusable advanced analytics for the Swiggy Market Intelligence project.

The dataset does not include a customer identifier or real order timestamp, so
customer-retention style methods are implemented at the restaurant-partner level
using Restaurant Name as the entity.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.arima.model import ARIMA


PRICE_COL = "Price (INR)"
DATE_COL = "Order Date"
ENTITY_COL = "Restaurant Name"


def classify_food_category(dish_names: pd.Series) -> pd.Series:
    """
    Classify dishes as Veg / Non-Veg using conservative keyword rules.

    Broad dish types like biryani or kebab are not treated as non-veg on their
    own because vegetarian variants are common.
    """
    dish_text = dish_names.fillna("").astype(str).str.lower()

    veg_override_pattern = (
        r"\b(?:veg|vegetarian|pure veg|eggless|no egg|without egg|paneer|mushroom|"
        r"aloo|gobi|dal|chole|soya|tofu)\b"
    )
    explicit_non_veg_pattern = r"\bnon[-\s]?veg\b"
    non_veg_pattern = (
        r"\b(?:chicken|mutton|fish|prawn|shrimp|seafood|meat|"
        r"lamb|beef|pork|crab|egg)\b"
    )

    explicit_non_veg = dish_text.str.contains(explicit_non_veg_pattern, regex=True, na=False)
    veg_override = dish_text.str.contains(veg_override_pattern, regex=True, na=False) & ~explicit_non_veg
    non_veg = explicit_non_veg | (
        dish_text.str.contains(non_veg_pattern, regex=True, na=False) & ~veg_override
    )
    return pd.Series(np.where(non_veg, "Non-Veg", "Veg"), index=dish_names.index)


def prepare_order_data(df: pd.DataFrame, include_synthetic_hour: bool = False) -> pd.DataFrame:
    """Return a copy of the orders data with common derived columns."""
    data = df.copy()
    data[DATE_COL] = pd.to_datetime(data[DATE_COL])
    data["Year-Month"] = data[DATE_COL].dt.to_period("M").astype(str)
    data["Quarter"] = data[DATE_COL].dt.to_period("Q").astype(str)
    data["DayName"] = data[DATE_COL].dt.day_name()
    data["DayOfWeek"] = data[DATE_COL].dt.dayofweek

    data["Value_Segment"] = pd.cut(
        data[PRICE_COL],
        bins=[0, 200, 500, 1000, float("inf")],
        labels=["Budget (<=200)", "Standard (201-500)", "Premium (501-1000)", "Luxury (>1000)"],
    )

    data["Food Category"] = classify_food_category(data["Dish Name"])

    if include_synthetic_hour and "Order Hour" not in data.columns:
        rng = np.random.default_rng(42)
        hour_probs = np.array(
            [
                0.005,
                0.005,
                0.005,
                0.005,
                0.005,
                0.005,
                0.020,
                0.030,
                0.040,
                0.040,
                0.060,
                0.100,
                0.120,
                0.100,
                0.050,
                0.040,
                0.030,
                0.050,
                0.060,
                0.120,
                0.120,
                0.100,
                0.080,
                0.040,
            ]
        )
        hour_probs = hour_probs / hour_probs.sum()
        data["Order Hour"] = rng.choice(24, size=len(data), p=hour_probs)
        data["Time Slot"] = pd.cut(
            data["Order Hour"],
            bins=[-1, 5, 10, 14, 17, 22, 23],
            labels=["Late Night", "Morning", "Lunch", "Afternoon", "Dinner", "Night"],
        )

    return data


def _score_percentile(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    pct = series.rank(pct=True, method="average")
    if not higher_is_better:
        pct = 1 - pct + (1 / len(series))
    return np.ceil(pct.clip(lower=0.2, upper=1) * 5).astype(int)


def calculate_rfm_segments(df: pd.DataFrame, entity_col: str = ENTITY_COL) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calculate restaurant-partner RFM scores and segment summary."""
    data = prepare_order_data(df)
    snapshot_date = data[DATE_COL].max() + pd.Timedelta(days=1)

    rfm = (
        data.groupby(entity_col)
        .agg(
            Last_Order=(DATE_COL, "max"),
            Recency_Days=(DATE_COL, lambda x: (snapshot_date - x.max()).days),
            Frequency=(PRICE_COL, "count"),
            Monetary=(PRICE_COL, "sum"),
            Avg_Order_Value=(PRICE_COL, "mean"),
            Avg_Rating=("Rating", "mean"),
        )
        .reset_index()
    )

    rfm["R_Score"] = _score_percentile(rfm["Recency_Days"], higher_is_better=False)
    rfm["F_Score"] = _score_percentile(rfm["Frequency"], higher_is_better=True)
    rfm["M_Score"] = _score_percentile(rfm["Monetary"], higher_is_better=True)
    rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]
    rfm["RFM_Code"] = (
        rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
    )

    def segment(row: pd.Series) -> str:
        if row["R_Score"] >= 4 and row["F_Score"] >= 4 and row["M_Score"] >= 4:
            return "Champions"
        if row["R_Score"] >= 3 and row["F_Score"] >= 4:
            return "Loyal Partners"
        if row["M_Score"] >= 4 and row["F_Score"] < 4:
            return "Big Spenders"
        if row["R_Score"] <= 2 and row["F_Score"] >= 3:
            return "At Risk"
        if row["R_Score"] <= 2:
            return "Hibernating"
        return "Emerging"

    rfm["RFM_Segment"] = rfm.apply(segment, axis=1)
    rfm = rfm.sort_values(["RFM_Score", "Monetary"], ascending=False).reset_index(drop=True)

    summary = (
        rfm.groupby("RFM_Segment")
        .agg(
            Entities=(entity_col, "count"),
            Avg_Recency_Days=("Recency_Days", "mean"),
            Avg_Frequency=("Frequency", "mean"),
            Total_Revenue=("Monetary", "sum"),
            Avg_RFM_Score=("RFM_Score", "mean"),
        )
        .round(2)
        .sort_values("Total_Revenue", ascending=False)
        .reset_index()
    )

    return rfm, summary


def calculate_restaurant_frequency_tiers(
    df: pd.DataFrame,
    entity_col: str = ENTITY_COL,
) -> pd.DataFrame:
    """Classify restaurants into Low / Medium / High volume tiers by order count."""
    data = prepare_order_data(df)
    frequency = (
        data.groupby(entity_col)
        .agg(
            Orders=(PRICE_COL, "count"),
            Revenue=(PRICE_COL, "sum"),
            Avg_Rating=("Rating", "mean"),
            City=("City", "first"),
            State=("State", "first"),
        )
        .round(2)
        .sort_values("Orders", ascending=False)
        .reset_index()
    )
    frequency["Frequency Tier"] = pd.cut(
        frequency["Orders"].rank(pct=True),
        bins=[0, 0.40, 0.80, 1.0],
        labels=["Low Volume (Bottom 40%)", "Medium Volume (40-80%)", "High Volume (Top 20%)"],
    )
    return frequency


def calculate_cohort_retention(df: pd.DataFrame, entity_col: str = ENTITY_COL) -> pd.DataFrame:
    """Build monthly restaurant-partner cohort retention matrix."""
    data = prepare_order_data(df)
    data["Order_Month"] = data[DATE_COL].dt.to_period("M")
    first_month = data.groupby(entity_col)["Order_Month"].transform("min")
    data["Cohort_Month"] = first_month
    data["Cohort_Index"] = (
        (data["Order_Month"].dt.year - data["Cohort_Month"].dt.year) * 12
        + (data["Order_Month"].dt.month - data["Cohort_Month"].dt.month)
    )

    cohort_counts = (
        data.groupby(["Cohort_Month", "Cohort_Index"])[entity_col]
        .nunique()
        .reset_index(name="Active Partners")
    )
    cohort_pivot = cohort_counts.pivot(
        index="Cohort_Month",
        columns="Cohort_Index",
        values="Active Partners",
    ).fillna(0)
    cohort_sizes = cohort_pivot[0].replace(0, np.nan)
    retention = cohort_pivot.divide(cohort_sizes, axis=0).mul(100).round(2)
    retention.insert(0, "Cohort Size", cohort_pivot[0].astype(int))
    retention.index = retention.index.astype(str)
    retention.columns = ["Cohort Size"] + [f"Month {int(col)}" for col in retention.columns[1:]]
    return retention.reset_index().rename(columns={"Cohort_Month": "Cohort Month"})


def run_statistical_tests(df: pd.DataFrame) -> pd.DataFrame:
    """Run Mann-Whitney U and ANOVA tests using available order fields."""
    data = prepare_order_data(df)
    results = []

    def add_result(test: str, metric: str, groups: str, statistic: float, p_value: float) -> None:
        significant = p_value < 0.05
        results.append(
            {
                "Test": test,
                "Metric": metric,
                "Groups Compared": groups,
                "Statistic": round(float(statistic), 4),
                "P-Value": round(float(p_value), 6),
                "Significant at 5%": "Yes" if significant else "No",
                "Interpretation": (
                    "Statistically significant difference detected"
                    if significant
                    else "No statistically significant difference detected"
                ),
            }
        )

    for metric in [PRICE_COL, "Rating"]:
        veg = data.loc[data["Food Category"] == "Veg", metric].dropna()
        non_veg = data.loc[data["Food Category"] == "Non-Veg", metric].dropna()
        if len(veg) > 1 and len(non_veg) > 1:
            statistic, p_value = stats.mannwhitneyu(veg, non_veg, alternative="two-sided")
            add_result("Mann-Whitney U", metric, "Veg vs Non-Veg", statistic, p_value)

    for metric in [PRICE_COL, "Rating"]:
        groups = [
            group[metric].dropna()
            for _, group in data.groupby("Value_Segment", observed=True)
            if len(group[metric].dropna()) > 1
        ]
        if len(groups) >= 2:
            statistic, p_value = stats.f_oneway(*groups)
            add_result("One-Way ANOVA", metric, "Budget / Standard / Premium / Luxury", statistic, p_value)

    city_groups = [
        group["Rating"].dropna()
        for _, group in data.groupby("City")
        if len(group["Rating"].dropna()) > 30
    ]
    if len(city_groups) >= 2:
        statistic, p_value = stats.f_oneway(*city_groups)
        add_result("One-Way ANOVA", "Rating", "Cities with 30+ orders", statistic, p_value)

    return pd.DataFrame(results)


def validate_revenue_forecast(df: pd.DataFrame, horizon: int = 3) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Validate monthly revenue forecasts against naive and moving-average baselines."""
    data = prepare_order_data(df)
    monthly = data.groupby("Year-Month")[PRICE_COL].sum().sort_index()
    monthly.index = pd.PeriodIndex(monthly.index, freq="M")

    if len(monthly) < 4:
        empty = pd.DataFrame()
        return empty, empty, empty

    holdout_size = min(2, max(1, len(monthly) // 4))
    train = monthly.iloc[:-holdout_size]
    test = monthly.iloc[-holdout_size:]

    predictions: dict[str, pd.Series] = {}
    predictions["Naive Baseline"] = pd.Series(train.iloc[-1], index=test.index)
    predictions["3-Month Moving Average"] = pd.Series(train.tail(min(3, len(train))).mean(), index=test.index)

    if len(train) >= 5:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                model = ARIMA(train.astype(float), order=(1, 1, 1))
                fitted = model.fit()
                predictions["ARIMA(1,1,1)"] = fitted.forecast(steps=holdout_size)
            except Exception:
                pass

    metric_rows = []
    validation = pd.DataFrame({"Month": test.index.astype(str), "Actual Revenue": test.values})
    for model_name, pred in predictions.items():
        pred = pd.Series(pred.values, index=test.index).clip(lower=0)
        validation[model_name] = pred.values
        mape = (np.abs((test - pred) / test)).mean() * 100
        rmse = np.sqrt(np.mean((test - pred) ** 2))
        metric_rows.append(
            {
                "Model": model_name,
                "MAPE (%)": round(float(mape), 2),
                "RMSE": round(float(rmse), 2),
                "Holdout Months": holdout_size,
            }
        )

    metrics = pd.DataFrame(metric_rows).sort_values("MAPE (%)").reset_index(drop=True)
    best_model = metrics.loc[0, "Model"]

    future_index = pd.period_range(monthly.index[-1] + 1, periods=horizon, freq="M")
    if best_model == "ARIMA(1,1,1)" and len(monthly) >= 5:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                fitted_full = ARIMA(monthly.astype(float), order=(1, 1, 1)).fit()
                future_values = fitted_full.forecast(steps=horizon).clip(lower=0).values
            except Exception:
                future_values = np.repeat(monthly.tail(min(3, len(monthly))).mean(), horizon)
    elif best_model == "Naive Baseline":
        future_values = np.repeat(monthly.iloc[-1], horizon)
    else:
        future_values = np.repeat(monthly.tail(min(3, len(monthly))).mean(), horizon)

    forecast = pd.DataFrame(
        {
            "Month": future_index.astype(str),
            "Forecast Revenue (INR)": np.round(future_values, 2),
            "Selected Model": best_model,
        }
    )

    return validation.round(2), metrics, forecast
