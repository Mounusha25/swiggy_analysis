"""Tab renderers for the Streamlit dashboard."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.preprocessing import MinMaxScaler

from analytics_models import (
    calculate_cohort_retention,
    calculate_rfm_segments,
    calculate_restaurant_frequency_tiers,
    run_statistical_tests,
    validate_revenue_forecast,
)
from sql_pipeline import QUERIES, run_query, setup_database


TAB_LABELS = [
    "📈 Overview",
    "🗺️ Geographic",
    "🎯 Segments",
    "📉 Trends",
    "💡 Insights",
    "🧭 Modeled Demand",
    "🧪 Advanced Analytics",
    "🗄️ SQL Pipeline",
    "📍 Expansion Strategy",
]


def render_tabs(df: pd.DataFrame, df_filtered: pd.DataFrame) -> None:
    tabs = st.tabs(TAB_LABELS)
    render_overview(tabs[0], df_filtered)
    render_geographic(tabs[1], df_filtered)
    render_segments(tabs[2], df_filtered)
    render_trends(tabs[3], df_filtered)
    render_insights(tabs[4], df_filtered)
    render_modeled_demand(tabs[5], df_filtered)
    render_advanced_analytics(tabs[6], df_filtered)
    render_sql_pipeline(tabs[7], df)
    render_expansion_strategy(tabs[8], df_filtered)


def render_overview(tab, df_filtered: pd.DataFrame) -> None:
    with tab:
        st.markdown('<h3 class="sub-header">Revenue Distribution</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            food_revenue = df_filtered.groupby("Food Category")["Price (INR)"].sum().reset_index()
            fig_food = px.pie(
                food_revenue,
                names="Food Category",
                values="Price (INR)",
                title="Revenue by Food Type",
                hole=0.4,
                color_discrete_map={"Veg": "#2ecc71", "Non-Veg": "#e74c3c"},
            )
            fig_food.update_traces(textinfo="label+percent")
            st.plotly_chart(fig_food, width="stretch")

        with col2:
            quarterly = (
                df_filtered.groupby("Quarter", as_index=False)
                .agg(
                    Sales=("Price (INR)", "sum"),
                    Orders=("Order Date", "count"),
                    Avg_Rating=("Rating", "mean"),
                )
                .sort_values("Quarter")
            )
            fig_quarterly = px.bar(
                quarterly,
                x="Quarter",
                y="Sales",
                title="Quarterly Performance",
                labels={"Sales": "Revenue (₹)"},
                color_discrete_sequence=["#667eea"],
            )
            st.plotly_chart(fig_quarterly, width="stretch")

        st.markdown('<h3 class="sub-header">Daily Sales Pattern</h3>', unsafe_allow_html=True)
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        daily_revenue = df_filtered.groupby("DayName")["Price (INR)"].sum().reindex(day_order)
        fig_daily = px.bar(
            x=daily_revenue.index,
            y=daily_revenue.values,
            title="Sales by Day of Week",
            labels={"x": "Day", "y": "Revenue (₹)"},
            color=daily_revenue.values,
            color_continuous_scale="Viridis",
        )
        fig_daily.update_layout(showlegend=False)
        st.plotly_chart(fig_daily, width="stretch")


def render_geographic(tab, df_filtered: pd.DataFrame) -> None:
    with tab:
        st.markdown('<h3 class="sub-header">Geographic Performance</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns([1.5, 1])

        with col1:
            state_revenue = (
                df_filtered.groupby("State", as_index=False)["Price (INR)"]
                .sum()
                .sort_values("Price (INR)", ascending=True)
                .tail(15)
            )
            fig_state = px.bar(
                state_revenue,
                x="Price (INR)",
                y="State",
                title="Top 15 States by Revenue",
                orientation="h",
                color="Price (INR)",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig_state, width="stretch")

        with col2:
            city_revenue = (
                df_filtered.groupby("City")["Price (INR)"]
                .sum()
                .nlargest(10)
                .sort_values()
                .reset_index()
            )
            fig_city = px.bar(
                city_revenue,
                x="Price (INR)",
                y="City",
                title="Top 10 Cities by Revenue",
                orientation="h",
                color="Price (INR)",
                color_continuous_scale="Greens",
            )
            st.plotly_chart(fig_city, width="stretch")

        st.markdown('<h3 class="sub-header">State Analysis</h3>', unsafe_allow_html=True)
        state_analysis = (
            df_filtered.groupby("State")
            .agg(
                Total_Revenue=("Price (INR)", "sum"),
                Orders=("Price (INR)", "count"),
                Avg_Price=("Price (INR)", "mean"),
                Avg_Rating=("Rating", "mean"),
            )
            .round(2)
            .sort_values("Total_Revenue", ascending=False)
            .head(10)
            .reset_index()
        )
        fig_state_scatter = px.scatter(
            state_analysis,
            x="Avg_Rating",
            y="Total_Revenue",
            size="Orders",
            color="Avg_Rating",
            hover_name="State",
            title="State Performance: Revenue vs Ratings",
            color_continuous_scale="RdYlGn",
        )
        st.plotly_chart(fig_state_scatter, width="stretch")


def render_segments(tab, df_filtered: pd.DataFrame) -> None:
    with tab:
        st.markdown('<h3 class="sub-header">Customer Segmentation</h3>', unsafe_allow_html=True)
        segment_df = df_filtered.copy()
        segment_analysis = (
            segment_df.groupby("Value_Segment", observed=True)
            .agg(Revenue=("Price (INR)", "sum"), Orders=("Price (INR)", "count"))
            .reset_index()
        )

        col1, col2 = st.columns(2)
        with col1:
            fig_segment_pie = px.pie(
                segment_analysis,
                names="Value_Segment",
                values="Revenue",
                title="Revenue by Order Value Segment",
                hole=0.4,
            )
            st.plotly_chart(fig_segment_pie, width="stretch")
        with col2:
            fig_segment_orders = px.bar(
                segment_analysis,
                x="Value_Segment",
                y="Orders",
                title="Order Count by Segment",
                color="Orders",
                color_continuous_scale="Plasma",
            )
            st.plotly_chart(fig_segment_orders, width="stretch")

        st.markdown('<h3 class="sub-header">Food Preference by State</h3>', unsafe_allow_html=True)
        state_food = (
            df_filtered.groupby(["State", "Food Category"])["Price (INR)"]
            .count()
            .reset_index(name="Orders")
        )
        top_states = df_filtered["State"].value_counts().head(10).index.tolist()
        heatmap_data = state_food[state_food["State"].isin(top_states)].pivot_table(
            index="State",
            columns="Food Category",
            values="Orders",
            fill_value=0,
        )
        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Food Category", y="State", color="Orders"),
            title="Food Type Preference by State",
            color_continuous_scale="YlOrRd",
        )
        st.plotly_chart(fig_heatmap, width="stretch")

        st.markdown('<h3 class="sub-header">Purchase Frequency Segmentation</h3>', unsafe_allow_html=True)
        st.caption("Restaurants are classified by order volume as a proxy for customer visit frequency.")
        rest_orders = calculate_restaurant_frequency_tiers(df_filtered)
        freq_summary = (
            rest_orders.groupby("Frequency Tier", observed=True)
            .agg(Restaurants=("Restaurant Name", "count"), Total_Orders=("Orders", "sum"))
            .reset_index()
        )
        col1, col2 = st.columns(2)
        with col1:
            fig_freq = px.bar(
                freq_summary,
                x="Frequency Tier",
                y="Total_Orders",
                title="Orders by Restaurant Frequency Tier",
                color="Frequency Tier",
                text="Total_Orders",
            )
            fig_freq.update_traces(texttemplate="%{text:,}", textposition="outside")
            st.plotly_chart(fig_freq, width="stretch")
        with col2:
            fig_freq_r = px.bar(
                freq_summary,
                x="Frequency Tier",
                y="Restaurants",
                title="Restaurant Count by Frequency Tier",
                color="Frequency Tier",
                text="Restaurants",
            )
            fig_freq_r.update_traces(texttemplate="%{text:,}", textposition="outside")
            st.plotly_chart(fig_freq_r, width="stretch")

def render_modeled_demand(tab, df_filtered: pd.DataFrame) -> None:
    with tab:
        st.markdown('<h3 class="sub-header">Modeled Demand Scenario</h3>', unsafe_allow_html=True)
        st.warning(
            "Synthetic analysis: the source data has `Order Date` but no real order-hour timestamp. "
            "The charts below use a reproducible lunch/dinner demand distribution to demonstrate "
            "how peak-hour analysis would work if timestamp data were available."
        )
        _render_time_of_day(df_filtered)


def _render_time_of_day(df_filtered: pd.DataFrame) -> None:
    st.markdown('<h3 class="sub-header">Synthetic Time-of-Day Order Patterns</h3>', unsafe_allow_html=True)
    st.caption("Modeled from a realistic delivery distribution; not observed order-hour data.")
    slot_order = ["Morning", "Lunch", "Afternoon", "Dinner", "Night", "Late Night"]
    tod = (
        df_filtered.groupby("Time Slot", observed=True)["Price (INR)"]
        .count()
        .reindex(slot_order)
        .reset_index(name="Orders")
    )

    col1, col2 = st.columns(2)
    with col1:
        fig_tod = px.bar(
            tod,
            x="Time Slot",
            y="Orders",
            title="Orders by Time Slot",
            color="Orders",
            color_continuous_scale="Sunset",
            text="Orders",
        )
        fig_tod.update_traces(texttemplate="%{text:,}", textposition="outside")
        st.plotly_chart(fig_tod, width="stretch")
    with col2:
        hour_dist = df_filtered.groupby("Order Hour")["Price (INR)"].count().reset_index()
        hour_dist.columns = ["Hour", "Orders"]
        fig_hour = px.bar(
            hour_dist,
            x="Hour",
            y="Orders",
            title="Orders by Hour of Day",
            color="Orders",
            color_continuous_scale="Plasma",
        )
        fig_hour.update_layout(showlegend=False, xaxis=dict(dtick=2))
        st.plotly_chart(fig_hour, width="stretch")

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_slot = (
        df_filtered.groupby(["DayName", "Time Slot"], observed=True)["Price (INR)"]
        .count()
        .reset_index(name="Orders")
    )
    pivot_ds = day_slot.pivot_table(index="DayName", columns="Time Slot", values="Orders", fill_value=0)
    pivot_ds = pivot_ds.reindex(day_order)
    pivot_ds = pivot_ds.reindex(columns=[col for col in slot_order if col in pivot_ds.columns])
    fig_ds_heatmap = px.imshow(
        pivot_ds,
        labels=dict(x="Time Slot", y="Day", color="Orders"),
        title="Order Density: Day of Week × Time Slot",
        color_continuous_scale="YlOrRd",
        aspect="auto",
    )
    st.plotly_chart(fig_ds_heatmap, width="stretch")


def render_trends(tab, df_filtered: pd.DataFrame) -> None:
    with tab:
        st.markdown('<h3 class="sub-header">Time Series Analysis</h3>', unsafe_allow_html=True)
        monthly_revenue = (
            df_filtered.groupby("Year-Month")["Price (INR)"].sum().reset_index().sort_values("Year-Month")
        )
        monthly_revenue["MA_3"] = monthly_revenue["Price (INR)"].rolling(window=3).mean()

        col1, col2 = st.columns([2, 1])
        with col1:
            fig_monthly = go.Figure()
            fig_monthly.add_trace(
                go.Scatter(
                    x=monthly_revenue["Year-Month"],
                    y=monthly_revenue["Price (INR)"],
                    mode="lines+markers",
                    name="Actual Revenue",
                    line=dict(color="lightblue", width=1),
                    fill="tozeroy",
                )
            )
            fig_monthly.add_trace(
                go.Scatter(
                    x=monthly_revenue["Year-Month"],
                    y=monthly_revenue["MA_3"],
                    mode="lines",
                    name="3-Month MA",
                    line=dict(color="red", width=2),
                )
            )
            fig_monthly.update_layout(
                title="Monthly Revenue Trend",
                xaxis_title="Month",
                yaxis_title="Revenue (₹)",
                hovermode="x unified",
                height=400,
            )
            st.plotly_chart(fig_monthly, width="stretch")

        with col2:
            if len(monthly_revenue) > 1:
                mom_growth = monthly_revenue["Price (INR)"].pct_change().iloc[-1] * 100
                avg_growth = monthly_revenue["Price (INR)"].pct_change().mean() * 100
                st.metric("Last Month MoM Growth", f"{mom_growth:.2f}%")
                st.metric("Avg Monthly Growth", f"{avg_growth:.2f}%")

        st.markdown('<h3 class="sub-header">Growth Rate Analysis</h3>', unsafe_allow_html=True)
        monthly_revenue["MoM_Growth"] = monthly_revenue["Price (INR)"].pct_change() * 100
        fig_growth = px.bar(
            monthly_revenue.dropna(),
            x="Year-Month",
            y="MoM_Growth",
            title="Month-over-Month Growth Rate",
            color="MoM_Growth",
            color_continuous_scale=["red", "yellow", "green"],
            color_continuous_midpoint=0,
        )
        st.plotly_chart(fig_growth, width="stretch")


def render_insights(tab, df_filtered: pd.DataFrame) -> None:
    with tab:
        st.markdown('<h3 class="sub-header">Strategic Insights</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📌 Pareto Analysis (80-20 Rule)")
            city_revenue = (
                df_filtered.groupby("City")["Price (INR)"].sum().sort_values(ascending=False).reset_index()
            )
            city_revenue["Cumulative_Percentage"] = (
                city_revenue["Price (INR)"].cumsum() / city_revenue["Price (INR)"].sum() * 100
            )
            city_revenue["City_Rank"] = range(1, len(city_revenue) + 1)
            top_80_cities = city_revenue[city_revenue["Cumulative_Percentage"] <= 80]
            st.markdown(
                f"""
                - **Top {len(top_80_cities)} cities** generate **80% of revenue**
                - **Total cities:** {len(city_revenue)}
                - **Concentration ratio:** {len(top_80_cities) / len(city_revenue) * 100:.1f}%
                """
            )
            fig_pareto = go.Figure()
            fig_pareto.add_trace(
                go.Bar(
                    x=city_revenue["City_Rank"][:20],
                    y=city_revenue["Price (INR)"][:20],
                    name="Revenue",
                    marker_color="lightblue",
                )
            )
            fig_pareto.add_trace(
                go.Scatter(
                    x=city_revenue["City_Rank"][:20],
                    y=city_revenue["Cumulative_Percentage"][:20],
                    name="Cumulative %",
                    yaxis="y2",
                    line=dict(color="red", width=3),
                    mode="lines+markers",
                )
            )
            fig_pareto.add_hline(y=80, line_dash="dash", line_color="green", yref="y2")
            fig_pareto.update_layout(
                title="Pareto Chart: Top 20 Cities",
                xaxis_title="City Rank",
                yaxis_title="Revenue (₹)",
                yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 100]),
                height=400,
            )
            st.plotly_chart(fig_pareto, width="stretch")

        with col2:
            st.subheader("📊 Correlation Analysis")
            correlation = df_filtered["Price (INR)"].corr(df_filtered["Rating"])
            st.metric("Price-Rating Correlation", f"{correlation:.3f}")
            if abs(correlation) < 0.3:
                st.info("💡 **Weak correlation** - Pricing doesn't strongly affect customer ratings")
            elif abs(correlation) < 0.7:
                st.info("💡 **Moderate correlation** - Some relationship between price and ratings")
            else:
                st.info("💡 **Strong correlation** - Price significantly impacts customer satisfaction")

            sample_size = min(1000, len(df_filtered))
            fig_scatter = px.scatter(
                df_filtered.sample(n=sample_size),
                x="Rating",
                y="Price (INR)",
                title="Price vs Rating (Sample)",
                trendline="ols",
                opacity=0.6,
            )
            st.plotly_chart(fig_scatter, width="stretch")

        _render_key_statistics(df_filtered)
        _render_menu_matrix(df_filtered)


def _render_key_statistics(df_filtered: pd.DataFrame) -> None:
    st.markdown('<h3 class="sub-header">📈 Key Statistics</h3>', unsafe_allow_html=True)
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    with stats_col1:
        st.metric("Unique States", df_filtered["State"].nunique())
    with stats_col2:
        st.metric("Unique Cities", df_filtered["City"].nunique())
    with stats_col3:
        st.metric("Unique Restaurants", df_filtered["Restaurant Name"].nunique())
    with stats_col4:
        st.metric("Unique Dishes", df_filtered["Dish Name"].nunique())


def _render_menu_matrix(df_filtered: pd.DataFrame) -> None:
    st.markdown('<h3 class="sub-header">🍽️ Menu Intelligence Matrix</h3>', unsafe_allow_html=True)
    st.caption("BCG-style quadrant framework: classifies food categories by revenue share vs. weighted rating.")

    exclude_pattern = (
        r"[()%&\d]|recommended|dotd|combo|deal|sale|fest|sharing|value|premium|"
        r"epic|exclusive|flash|limited|group|protein|session|special|collection|"
        r"tub|scooped|mcsaver|royal|jumbo|bucket|family|party|pack|offer|free|"
        r"discount|saving|upto|up to|newly|launched"
    )
    matrix_df = df_filtered.copy()
    matrix_df = matrix_df[
        ~matrix_df["Category"].str.contains(r"[()%&\d]", regex=True, na=False)
        & ~matrix_df["Category"].str.lower().str.contains(exclude_pattern, regex=True, na=False)
    ].copy()
    matrix_df["_Cat_clean"] = (
        matrix_df["Category"]
        .str.strip()
        .str.title()
        .str.replace(r"\bCakes\b", "Cake", regex=True)
        .str.replace(r"\bBurgers\b", "Burger", regex=True)
        .str.replace(r"\bRolls\b", "Roll", regex=True)
        .str.replace(r"\bPizzas\b", "Pizza", regex=True)
        .str.replace(r"\bBeverages\b", "Beverage", regex=True)
        .str.replace(r"\bNoodles\b", "Noodle", regex=True)
    )

    cat_stats = (
        matrix_df.groupby("_Cat_clean")
        .agg(
            Revenue=("Price (INR)", "sum"),
            Orders=("Price (INR)", "count"),
            Weighted_Rating=(
                "Rating",
                lambda x: np.average(x, weights=matrix_df.loc[x.index, "Rating Count"].clip(lower=1)),
            ),
        )
        .reset_index()
        .rename(columns={"_Cat_clean": "Category"})
    )
    cat_stats = cat_stats[cat_stats["Orders"] >= 100].nlargest(15, "Revenue").reset_index(drop=True)
    if cat_stats.empty:
        st.warning("Not enough category volume in the current filters to build the menu matrix.")
        return

    cat_stats["Revenue_Share"] = cat_stats["Revenue"] / cat_stats["Revenue"].sum() * 100
    rev_median = cat_stats["Revenue_Share"].median()
    rating_median = cat_stats["Weighted_Rating"].median()

    def assign_quadrant(row: pd.Series) -> str:
        hi_rev = row["Revenue_Share"] >= rev_median
        hi_rating = row["Weighted_Rating"] >= rating_median
        if hi_rev and hi_rating:
            return "Stars"
        if hi_rev:
            return "Cash Cows"
        if hi_rating:
            return "Hidden Gems"
        return "Review Needed"

    cat_stats["Quadrant"] = cat_stats.apply(assign_quadrant, axis=1)
    fig_mim = px.scatter(
        cat_stats,
        x="Revenue_Share",
        y="Weighted_Rating",
        size="Orders",
        color="Quadrant",
        text="Category",
        title="Menu Intelligence Matrix: Category Positioning",
        labels={"Revenue_Share": "Revenue Share (%)", "Weighted_Rating": "Weighted Rating"},
        color_discrete_map={
            "Stars": "#FFD700",
            "Hidden Gems": "#00BFFF",
            "Cash Cows": "#32CD32",
            "Review Needed": "#FF4500",
        },
    )
    fig_mim.add_vline(x=rev_median, line_dash="dash", line_color="gray", annotation_text="Revenue Median")
    fig_mim.add_hline(y=rating_median, line_dash="dash", line_color="gray", annotation_text="Rating Median")
    fig_mim.update_traces(textposition="top center")
    fig_mim.update_layout(height=550)
    st.plotly_chart(fig_mim, width="stretch")

    st.dataframe(
        cat_stats[["Category", "Quadrant", "Revenue_Share", "Weighted_Rating", "Orders"]]
        .sort_values("Revenue_Share", ascending=False)
        .rename(columns={"Revenue_Share": "Revenue Share (%)", "Weighted_Rating": "Weighted Rating"})
        .reset_index(drop=True),
        width="stretch",
    )


def render_advanced_analytics(tab, df_filtered: pd.DataFrame) -> None:
    with tab:
        st.markdown('<h3 class="sub-header">🧪 Advanced Analytics</h3>', unsafe_allow_html=True)
        st.info(
            "RFM and cohort retention need a stable customer identifier. This dataset has no Customer ID, "
            "so the dashboard implements these methods at the restaurant-partner level using `Restaurant Name`."
        )
        if df_filtered.empty:
            st.warning("No rows match the current filters. Widen the filters to run advanced analytics.")
            return

        rfm_df, rfm_summary = calculate_rfm_segments(df_filtered)
        cohort_df = calculate_cohort_retention(df_filtered)
        stats_df = run_statistical_tests(df_filtered)
        validation_df, forecast_metrics, forecast_df = validate_revenue_forecast(df_filtered)

        st.markdown('<h3 class="sub-header">RFM Partner Segmentation</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            fig_rfm = px.bar(
                rfm_summary,
                x="RFM_Segment",
                y="Entities",
                color="RFM_Segment",
                title="Restaurant Partners by RFM Segment",
            )
            st.plotly_chart(fig_rfm, width="stretch")
        with col2:
            st.dataframe(
                rfm_summary.rename(
                    columns={
                        "Entities": "Restaurants",
                        "Total_Revenue": "Total Revenue (INR)",
                        "Avg_RFM_Score": "Avg RFM Score",
                    }
                ),
                width="stretch",
            )

        st.markdown("**Top RFM-ranked partners**")
        st.dataframe(
            rfm_df[
                [
                    "Restaurant Name",
                    "RFM_Segment",
                    "RFM_Code",
                    "RFM_Score",
                    "Recency_Days",
                    "Frequency",
                    "Monetary",
                    "Avg_Rating",
                ]
            ]
            .head(25)
            .rename(
                columns={
                    "RFM_Segment": "Segment",
                    "RFM_Code": "RFM Code",
                    "RFM_Score": "RFM Score",
                    "Recency_Days": "Recency Days",
                    "Monetary": "Revenue (INR)",
                    "Avg_Rating": "Avg Rating",
                }
            ),
            width="stretch",
        )

        st.markdown('<h3 class="sub-header">Monthly Cohort Retention</h3>', unsafe_allow_html=True)
        st.caption("Retention is the percentage of restaurants from each first-active month that remain active later.")
        heatmap_df = cohort_df.set_index("Cohort Month").drop(columns=["Cohort Size"], errors="ignore")
        fig_cohort = px.imshow(
            heatmap_df,
            text_auto=".1f",
            aspect="auto",
            color_continuous_scale="Blues",
            labels=dict(x="Months Since First Order", y="Cohort Month", color="Retention %"),
            title="Restaurant Partner Cohort Retention (%)",
        )
        fig_cohort.update_layout(height=450)
        st.plotly_chart(fig_cohort, width="stretch")
        st.dataframe(cohort_df, width="stretch")

        st.markdown('<h3 class="sub-header">Statistical Testing</h3>', unsafe_allow_html=True)
        st.caption("Mann-Whitney U compares Veg vs Non-Veg; ANOVA tests differences across value tiers and cities.")
        st.dataframe(stats_df, width="stretch")

        _render_forecast_validation(validation_df, forecast_metrics, forecast_df)


def _render_forecast_validation(
    validation_df: pd.DataFrame,
    forecast_metrics: pd.DataFrame,
    forecast_df: pd.DataFrame,
) -> None:
    st.markdown('<h3 class="sub-header">Forecast Validation</h3>', unsafe_allow_html=True)
    st.caption("ARIMA is validated against naive and 3-month moving-average baselines using holdout months.")
    if validation_df.empty:
        st.warning("Not enough monthly history to validate a forecast with the current filters.")
        return

    fig_forecast = go.Figure()
    fig_forecast.add_trace(
        go.Scatter(
            x=validation_df["Month"],
            y=validation_df["Actual Revenue"],
            mode="lines+markers",
            name="Actual Revenue",
        )
    )
    for model_name in [col for col in validation_df.columns if col not in ["Month", "Actual Revenue"]]:
        fig_forecast.add_trace(
            go.Scatter(
                x=validation_df["Month"],
                y=validation_df[model_name],
                mode="lines+markers",
                name=model_name,
            )
        )
    fig_forecast.update_layout(
        title="Holdout Forecast Validation",
        xaxis_title="Month",
        yaxis_title="Revenue (INR)",
        hovermode="x unified",
        height=420,
    )
    st.plotly_chart(fig_forecast, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Model Accuracy**")
        st.dataframe(forecast_metrics, width="stretch")
    with col2:
        st.markdown("**Next 3-Month Forecast**")
        st.dataframe(forecast_df, width="stretch")


def render_sql_pipeline(tab, df: pd.DataFrame) -> None:
    with tab:
        st.markdown('<h3 class="sub-header">🗄️ SQL Analytics Pipeline</h3>', unsafe_allow_html=True)
        st.info(
            "Raw order data is loaded from `swiggy_data.xlsx` into a SQLite database. "
            "All analytics below are produced by SQL queries running against that database."
        )
        with st.spinner("Initialising SQLite database from swiggy_data.xlsx…"):
            db_path = setup_database()
        st.success(f"Database ready: `swiggy.db`  |  {len(df):,} rows loaded into `orders` table")

        query_name = st.selectbox("Select an analytics query:", list(QUERIES.keys()))
        selected = QUERIES[query_name]
        st.markdown(f"**Description:** {selected['description']}")
        with st.expander("View SQL", expanded=True):
            st.code(selected["sql"], language="sql")

        result_df = run_query(selected["sql"], db_path)
        st.markdown(f"**Results — {len(result_df)} rows**")
        st.dataframe(result_df, width="stretch")
        st.download_button(
            label="📥 Download query result as CSV",
            data=result_df.to_csv(index=False).encode(),
            file_name=f"{query_name.replace(' ', '_').lower()}.csv",
            mime="text/csv",
        )


def render_expansion_strategy(tab, df_filtered: pd.DataFrame) -> None:
    with tab:
        _render_city_expansion(df_filtered)
        _render_restaurant_health(df_filtered)


def _render_city_expansion(df_filtered: pd.DataFrame) -> None:
    st.markdown('<h3 class="sub-header">🏙️ City Expansion Opportunity Index</h3>', unsafe_allow_html=True)
    st.caption(
        "A 4-signal composite model (0-100): Revenue Growth (30%) + Weighted Rating (25%) "
        "+ Order Density (25%) + Category Diversity (20%)."
    )
    analysis_df = df_filtered.copy()
    analysis_df["_Order_Date_dt"] = pd.to_datetime(analysis_df["Order Date"])
    mid_date = analysis_df["_Order_Date_dt"].min() + (
        analysis_df["_Order_Date_dt"].max() - analysis_df["_Order_Date_dt"].min()
    ) / 2
    city_h1 = analysis_df[analysis_df["_Order_Date_dt"] < mid_date].groupby("City")["Price (INR)"].sum()
    city_h2 = analysis_df[analysis_df["_Order_Date_dt"] >= mid_date].groupby("City")["Price (INR)"].sum()

    city_agg = (
        analysis_df.groupby("City")
        .agg(
            Orders=("Price (INR)", "count"),
            Revenue=("Price (INR)", "sum"),
            Weighted_Rating=(
                "Rating",
                lambda x: np.average(x, weights=analysis_df.loc[x.index, "Rating Count"].clip(lower=1)),
            ),
            Restaurants=("Restaurant Name", "nunique"),
            Categories=("Category", "nunique"),
        )
        .reset_index()
    )
    city_agg["Growth_Rate"] = (
        city_agg["City"].map(city_h2).fillna(0) / city_agg["City"].map(city_h1).replace(0, np.nan).fillna(1)
    ) - 1
    city_agg["Order_Density"] = city_agg["Orders"] / city_agg["Restaurants"].replace(0, np.nan)
    city_agg["Cat_Diversity"] = city_agg["Categories"]

    features = ["Growth_Rate", "Weighted_Rating", "Order_Density", "Cat_Diversity"]
    city_agg[features] = city_agg[features].fillna(0)
    norm = MinMaxScaler().fit_transform(city_agg[features])
    city_agg["Opportunity_Score"] = (
        norm[:, 0] * 0.30 + norm[:, 1] * 0.25 + norm[:, 2] * 0.25 + norm[:, 3] * 0.20
    ) * 100
    city_agg = city_agg.sort_values("Opportunity_Score", ascending=False).reset_index(drop=True)

    rev_med = city_agg["Revenue"].median()
    opp_med = city_agg["Opportunity_Score"].median()
    city_agg["City_Tier"] = city_agg.apply(
        lambda row: _city_quadrant(row, revenue_median=rev_med, opportunity_median=opp_med),
        axis=1,
    )

    fig_a1 = px.scatter(
        city_agg,
        x="Revenue",
        y="Opportunity_Score",
        size="Orders",
        color="City_Tier",
        hover_name="City",
        title="City Expansion Opportunity Index",
        labels={"Revenue": "Total Revenue (INR)", "Opportunity_Score": "Opportunity Score (0-100)"},
        color_discrete_map={
            "Stars": "#FFD700",
            "Untapped": "#00BFFF",
            "Emerging": "#32CD32",
            "Low Priority": "#D3D3D3",
        },
    )
    fig_a1.add_vline(x=rev_med, line_dash="dash", line_color="gray")
    fig_a1.add_hline(y=opp_med, line_dash="dash", line_color="gray")
    fig_a1.update_layout(height=550)
    st.plotly_chart(fig_a1, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        fig_top10 = px.bar(
            city_agg.head(10),
            x="Opportunity_Score",
            y="City",
            orientation="h",
            color="Opportunity_Score",
            color_continuous_scale="Blues",
            title="Top 10 Cities by Opportunity Score",
        )
        fig_top10.update_layout(height=400, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_top10, width="stretch")
    with col2:
        st.markdown("**Top 10 Expansion Targets**")
        st.dataframe(
            city_agg[["City", "Opportunity_Score", "City_Tier", "Orders", "Revenue"]]
            .head(10)
            .rename(columns={"Opportunity_Score": "Score", "City_Tier": "Tier"})
            .reset_index(drop=True),
            width="stretch",
        )


def _city_quadrant(row: pd.Series, revenue_median: float, opportunity_median: float) -> str:
    hi_rev = row["Revenue"] >= revenue_median
    hi_opp = row["Opportunity_Score"] >= opportunity_median
    if hi_rev and hi_opp:
        return "Stars"
    if not hi_rev and hi_opp:
        return "Untapped"
    if hi_rev:
        return "Emerging"
    return "Low Priority"


def _render_restaurant_health(df_filtered: pd.DataFrame) -> None:
    st.markdown('<h3 class="sub-header">🏥 Restaurant Health Score</h3>', unsafe_allow_html=True)
    st.caption(
        "Composite viability score (0-100): Revenue 40% + Rating 30% + Orders 20% + Recency 10%."
    )
    analysis_df = df_filtered.copy()
    analysis_df["_Order_Date_dt"] = pd.to_datetime(analysis_df["Order Date"])
    snapshot_date = analysis_df["_Order_Date_dt"].max() + pd.Timedelta(days=1)

    rest_agg = (
        analysis_df.groupby("Restaurant Name")
        .agg(
            Revenue=("Price (INR)", "sum"),
            Orders=("Price (INR)", "count"),
            Weighted_Rating=(
                "Rating",
                lambda x: np.average(x, weights=analysis_df.loc[x.index, "Rating Count"].clip(lower=1)),
            ),
            Last_Order=("_Order_Date_dt", "max"),
        )
        .reset_index()
    )
    rest_agg["Revenue_Share"] = rest_agg["Revenue"] / rest_agg["Revenue"].sum() * 100
    rest_agg["Recency_Days"] = (snapshot_date - rest_agg["Last_Order"]).dt.days

    scaler = MinMaxScaler()
    rest_agg[["Rev_N", "Rating_N", "Orders_N"]] = scaler.fit_transform(
        rest_agg[["Revenue_Share", "Weighted_Rating", "Orders"]]
    )
    rest_agg["Recency_N"] = 1 - scaler.fit_transform(rest_agg[["Recency_Days"]])
    rest_agg["Health_Score"] = (
        rest_agg["Rev_N"] * 0.40
        + rest_agg["Rating_N"] * 0.30
        + rest_agg["Orders_N"] * 0.20
        + rest_agg["Recency_N"] * 0.10
    ) * 100
    rest_agg["Health_Tier"] = rest_agg["Health_Score"].apply(_health_tier)

    col1, col2 = st.columns(2)
    with col1:
        fig_top_r = px.bar(
            rest_agg.nlargest(15, "Health_Score"),
            x="Health_Score",
            y="Restaurant Name",
            orientation="h",
            color="Health_Score",
            color_continuous_scale="Greens",
            title="Top 15 Champion Restaurants",
        )
        fig_top_r.update_layout(height=500, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_top_r, width="stretch")
    with col2:
        fig_bot_r = px.bar(
            rest_agg.nsmallest(15, "Health_Score"),
            x="Health_Score",
            y="Restaurant Name",
            orientation="h",
            color="Health_Score",
            color_continuous_scale="Reds_r",
            title="Bottom 15 At-Risk Restaurants",
        )
        fig_bot_r.update_layout(height=500, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_bot_r, width="stretch")

    tier_counts = rest_agg["Health_Tier"].value_counts().reset_index()
    tier_counts.columns = ["Tier", "Count"]
    fig_tier = px.bar(
        tier_counts,
        x="Tier",
        y="Count",
        color="Tier",
        color_discrete_map={
            "Champion": "#FFD700",
            "Healthy": "#32CD32",
            "At Risk": "#FFA500",
            "Critical": "#FF4500",
        },
        title="Restaurant Health Tier Distribution",
    )
    st.plotly_chart(fig_tier, width="stretch")


def _health_tier(score: float) -> str:
    if score >= 75:
        return "Champion"
    if score >= 50:
        return "Healthy"
    if score >= 25:
        return "At Risk"
    return "Critical"
