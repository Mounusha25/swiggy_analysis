"""
generate_excel_report.py
------------------------
Generates a formatted 13-sheet Excel KPI report from Swiggy order data
using openpyxl.

Standalone usage:
    python3 generate_excel_report.py
    # → writes swiggy_kpi_report.xlsx in the current directory

Imported by app.py to provide a Streamlit download button.
"""

import io
import os
from datetime import datetime

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------------
# Brand palette
# ---------------------------------------------------------------------------
ORANGE = "FF6B35"
DARK = "2D3142"
LIGHT_GRAY = "F2F2F2"
WHITE = "FFFFFF"


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

def _sheet_title(ws, row: int, n_cols: int, text: str, bg: str = ORANGE) -> None:
    last_col = get_column_letter(n_cols)
    ws.merge_cells(f"A{row}:{last_col}{row}")
    cell = ws[f"A{row}"]
    cell.value = text
    cell.font = Font(bold=True, color=WHITE, size=13)
    cell.fill = PatternFill(fill_type="solid", fgColor=bg)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 30


def _col_headers(ws, row: int, headers: list) -> None:
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=row, column=i, value=h)
        c.font = Font(bold=True, color=WHITE, size=10)
        c.fill = PatternFill(fill_type="solid", fgColor=DARK)
        c.alignment = Alignment(horizontal="center")


def _write_df(ws, df: pd.DataFrame, start_row: int) -> None:
    for r_idx, row in enumerate(df.itertuples(index=False), start_row):
        for c_idx, val in enumerate(row, 1):
            # Convert numpy types to native Python for openpyxl compatibility
            if isinstance(val, (np.integer,)):
                val = int(val)
            elif isinstance(val, (np.floating,)):
                val = float(val)
            c = ws.cell(row=r_idx, column=c_idx, value=val)
            c.alignment = Alignment(horizontal="center")
            if r_idx % 2 == 0:
                c.fill = PatternFill(fill_type="solid", fgColor=LIGHT_GRAY)


def _autofit(ws, df: pd.DataFrame, pad: int = 4) -> None:
    for i, col in enumerate(df.columns, 1):
        header_len = len(str(col))
        data_len = df[col].astype(str).map(len).max() if len(df) else 0
        ws.column_dimensions[get_column_letter(i)].width = min(
            max(header_len, data_len) + pad, 42
        )


def _build_sheet(wb: Workbook, sheet_name: str, title: str, df: pd.DataFrame) -> None:
    ws = wb.create_sheet(sheet_name)
    _sheet_title(ws, 1, len(df.columns), title)
    _col_headers(ws, 2, df.columns.tolist())
    _write_df(ws, df, 3)
    _autofit(ws, df)


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def generate_report(df: pd.DataFrame, output_path: str = None):
    """
    Build a 13-sheet Excel KPI workbook from the Swiggy orders DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Raw or preprocessed Swiggy order data.
    output_path : str, optional
        If provided, the workbook is saved to this path and the path is returned.
        If None (default), the workbook bytes are returned for Streamlit download.

    Returns
    -------
    str | bytes
        File path (if output_path given) or raw bytes.
    """
    df = df.copy()

    # --- Preprocessing (idempotent — safe to run even if columns already exist) ---
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Year-Month"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
    df["DayName"] = df["Order Date"].dt.day_name()
    df["DayOfWeek"] = df["Order Date"].dt.dayofweek

    df["Value_Segment"] = pd.cut(
        df["Price (INR)"],
        bins=[0, 200, 500, 1000, float("inf")],
        labels=["Budget (<=200)", "Standard (201-500)", "Premium (501-1000)", "Luxury (>1000)"],
    )

    # Synthetic Order Hour — reproducible distribution (lunch + dinner peaks)
    rng = np.random.default_rng(42)
    hour_probs = np.array(
        [0.005, 0.005, 0.005, 0.005, 0.005, 0.005,   # 00-05 late night
         0.020, 0.030, 0.040,                          # 06-08 morning
         0.040, 0.060,                                 # 09-10 brunch
         0.100, 0.120, 0.100,                          # 11-13 lunch peak
         0.050, 0.040, 0.030,                          # 14-16 afternoon
         0.050, 0.060,                                 # 17-18 early evening
         0.120, 0.120, 0.100, 0.080,                   # 19-22 dinner peak
         0.040],                                       # 23    night
    )
    hour_probs = hour_probs / hour_probs.sum()
    df["Order Hour"] = rng.choice(24, size=len(df), p=hour_probs)
    df["Time Slot"] = pd.cut(
        df["Order Hour"],
        bins=[-1, 5, 10, 14, 17, 22, 23],
        labels=["Late Night", "Morning", "Lunch", "Afternoon", "Dinner", "Night"],
    )

    wb = Workbook()
    wb.remove(wb.active)  # remove default blank sheet

    # ── Sheet 1 : Summary KPIs ─────────────────────────────────────────────
    ws = wb.create_sheet("1. Summary KPIs")
    monthly_rev = df.groupby("Year-Month")["Price (INR)"].sum().sort_index()
    mom = (
        (monthly_rev.iloc[-1] - monthly_rev.iloc[-2]) / monthly_rev.iloc[-2] * 100
        if len(monthly_rev) > 1 else 0.0
    )
    avg_growth = monthly_rev.pct_change().mean() * 100

    _sheet_title(ws, 1, 3, "Swiggy Sales Analytics — Executive KPI Summary")
    kpis = [
        ("KPI", "Value", "Notes"),
        ("Total Revenue (INR)", f"{df['Price (INR)'].sum():,.0f}", "Sum of all order values"),
        ("Total Orders", f"{len(df):,}", "Count of all order records"),
        ("Avg Order Value (INR)", f"{df['Price (INR)'].mean():,.2f}", "Mean basket size"),
        ("Avg Rating", f"{df['Rating'].mean():.2f} / 5.0", "Mean customer satisfaction"),
        ("MoM Growth — Last Month", f"{mom:.2f}%", "Month-over-month revenue change"),
        ("Avg Monthly Growth Rate", f"{avg_growth:.2f}%", "Average MoM growth"),
        ("Unique States", str(df["State"].nunique()), "Geographic coverage"),
        ("Unique Cities", str(df["City"].nunique()), "City-level reach"),
        ("Unique Restaurants", str(df["Restaurant Name"].nunique()), "Partner count"),
        ("Unique Dishes", str(df["Dish Name"].nunique()), "Menu diversity"),
        ("Unique Categories", str(df["Category"].nunique()), "Cuisine diversity"),
        ("Total Rating Count", f"{df['Rating Count'].sum():,}", "Total customer reviews"),
        ("Report Generated", datetime.now().strftime("%Y-%m-%d %H:%M"), ""),
    ]
    for r_i, row_data in enumerate(kpis, 3):
        for c_i, val in enumerate(row_data, 1):
            c = ws.cell(row=r_i, column=c_i, value=val)
            if r_i == 3:
                c.font = Font(bold=True, color=WHITE, size=10)
                c.fill = PatternFill(fill_type="solid", fgColor=DARK)
                c.alignment = Alignment(horizontal="center")
            else:
                c.alignment = Alignment(horizontal="left")
                if r_i % 2 == 0:
                    c.fill = PatternFill(fill_type="solid", fgColor=LIGHT_GRAY)
    for col_letter, width in zip(["A", "B", "C"], [35, 22, 38]):
        ws.column_dimensions[col_letter].width = width

    # ── Sheet 2 : Monthly Trend ────────────────────────────────────────────
    monthly_df = (
        df.groupby("Year-Month")
        .agg(Orders=("Price (INR)", "count"),
             Revenue=("Price (INR)", "sum"),
             Avg_Order_Value=("Price (INR)", "mean"),
             Avg_Rating=("Rating", "mean"))
        .round(2)
        .reset_index()
    )
    monthly_df.columns = ["Month", "Orders", "Revenue (INR)", "Avg Order Value (INR)", "Avg Rating"]
    monthly_df["MoM Growth (%)"] = monthly_df["Revenue (INR)"].pct_change().mul(100).round(2)
    _build_sheet(wb, "2. Monthly Trend", "Monthly Revenue Trend & Seasonality", monthly_df)

    # ── Sheet 3 : Quarterly Performance ───────────────────────────────────
    qdf = (
        df.groupby("Quarter")
        .agg(Orders=("Price (INR)", "count"),
             Revenue=("Price (INR)", "sum"),
             Avg_Order_Value=("Price (INR)", "mean"),
             Avg_Rating=("Rating", "mean"))
        .round(2)
        .reset_index()
    )
    qdf.columns = ["Quarter", "Orders", "Revenue (INR)", "Avg Order Value (INR)", "Avg Rating"]
    _build_sheet(wb, "3. Quarterly Performance", "Quarterly Sales Performance", qdf)

    # ── Sheet 4 : Top States ──────────────────────────────────────────────
    state_df = (
        df.groupby("State")
        .agg(Orders=("Price (INR)", "count"),
             Revenue=("Price (INR)", "sum"),
             Avg_Order_Value=("Price (INR)", "mean"),
             Avg_Rating=("Rating", "mean"),
             Total_Rating_Count=("Rating Count", "sum"))
        .round(2)
        .sort_values("Revenue", ascending=False)
        .reset_index()
    )
    state_df.columns = [
        "State", "Orders", "Revenue (INR)", "Avg Order Value (INR)",
        "Avg Rating", "Total Rating Count"
    ]
    _build_sheet(wb, "4. Top States", "State-wise Revenue Performance", state_df)

    # ── Sheet 5 : Top Cities ──────────────────────────────────────────────
    city_df = (
        df.groupby(["City", "State"])
        .agg(Orders=("Price (INR)", "count"),
             Revenue=("Price (INR)", "sum"),
             Avg_Order_Value=("Price (INR)", "mean"),
             Avg_Rating=("Rating", "mean"))
        .round(2)
        .sort_values("Revenue", ascending=False)
        .head(30)
        .reset_index()
    )
    city_df.columns = ["City", "State", "Orders", "Revenue (INR)", "Avg Order Value (INR)", "Avg Rating"]
    _build_sheet(wb, "5. Top Cities", "Top 30 Cities by Revenue", city_df)

    # ── Sheet 6 : Top Dishes ──────────────────────────────────────────────
    dish_df = (
        df.groupby("Dish Name")
        .agg(Orders=("Price (INR)", "count"),
             Revenue=("Price (INR)", "sum"),
             Avg_Price=("Price (INR)", "mean"),
             Avg_Rating=("Rating", "mean"))
        .round(2)
        .sort_values("Revenue", ascending=False)
        .head(30)
        .reset_index()
    )
    dish_df.columns = ["Dish Name", "Orders", "Revenue (INR)", "Avg Price (INR)", "Avg Rating"]
    _build_sheet(wb, "6. Top Dishes", "Top 30 Dishes by Revenue", dish_df)

    # ── Sheet 7 : Category Mix ────────────────────────────────────────────
    cat_df = (
        df.groupby("Category")
        .agg(Orders=("Price (INR)", "count"),
             Revenue=("Price (INR)", "sum"),
             Avg_Price=("Price (INR)", "mean"),
             Avg_Rating=("Rating", "mean"))
        .round(2)
        .sort_values("Revenue", ascending=False)
        .reset_index()
    )
    cat_df.columns = ["Category", "Orders", "Revenue (INR)", "Avg Price (INR)", "Avg Rating"]
    cat_df["Revenue Share (%)"] = (
        cat_df["Revenue (INR)"] / cat_df["Revenue (INR)"].sum() * 100
    ).round(2)
    _build_sheet(wb, "7. Category Mix", "Food Category Revenue Mix", cat_df)

    # ── Sheet 8 : Customer Segments ───────────────────────────────────────
    seg_df = (
        df.groupby("Value_Segment", observed=True)
        .agg(Orders=("Price (INR)", "count"),
             Revenue=("Price (INR)", "sum"),
             Avg_Price=("Price (INR)", "mean"),
             Avg_Rating=("Rating", "mean"))
        .round(2)
        .reset_index()
    )
    seg_df.columns = ["Segment", "Orders", "Revenue (INR)", "Avg Order Value (INR)", "Avg Rating"]
    seg_df["Revenue Share (%)"] = (seg_df["Revenue (INR)"] / seg_df["Revenue (INR)"].sum() * 100).round(2)
    seg_df["Order Share (%)"] = (seg_df["Orders"] / seg_df["Orders"].sum() * 100).round(2)
    _build_sheet(wb, "8. Customer Segments", "Customer Segmentation by Basket Value", seg_df)

    # ── Sheet 9 : Pareto Analysis ─────────────────────────────────────────
    pareto_df = (
        df.groupby("City")["Price (INR)"].sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    pareto_df.columns = ["City", "Revenue (INR)"]
    pareto_df["Cumulative Revenue (INR)"] = pareto_df["Revenue (INR)"].cumsum()
    pareto_df["Cumulative % of Revenue"] = (
        pareto_df["Cumulative Revenue (INR)"] / pareto_df["Revenue (INR)"].sum() * 100
    ).round(2)
    pareto_df["City Rank"] = range(1, len(pareto_df) + 1)
    n80 = (pareto_df["Cumulative % of Revenue"] <= 80).sum()
    _build_sheet(
        wb, "9. Pareto Analysis",
        f"Pareto Analysis — {n80} cities drive 80% of total revenue",
        pareto_df,
    )

    # ── Sheet 10 : Day of Week ────────────────────────────────────────────
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_df = (
        df.groupby("DayName")
        .agg(Orders=("Price (INR)", "count"),
             Revenue=("Price (INR)", "sum"),
             Avg_Order_Value=("Price (INR)", "mean"),
             Avg_Rating=("Rating", "mean"))
        .round(2)
        .reindex(day_order)
        .reset_index()
    )
    dow_df.columns = ["Day of Week", "Orders", "Revenue (INR)", "Avg Order Value (INR)", "Avg Rating"]
    _build_sheet(wb, "10. Day of Week", "Sales Patterns by Day of Week", dow_df)

    # ── Sheet 11 : Time of Day ────────────────────────────────────────────
    slot_order = ["Morning", "Lunch", "Afternoon", "Dinner", "Night", "Late Night"]
    tod_df = (
        df.groupby("Time Slot", observed=True)
        .agg(Orders=("Price (INR)", "count"),
             Revenue=("Price (INR)", "sum"),
             Avg_Order_Value=("Price (INR)", "mean"),
             Avg_Rating=("Rating", "mean"))
        .round(2)
        .reindex(slot_order)
        .reset_index()
    )
    tod_df.columns = ["Time Slot", "Orders", "Revenue (INR)", "Avg Order Value (INR)", "Avg Rating"]
    tod_df["Order Share (%)"] = (tod_df["Orders"] / tod_df["Orders"].sum() * 100).round(2)
    _build_sheet(
        wb, "11. Time of Day",
        "Order Patterns by Time of Day (modelled distribution)",
        tod_df,
    )

    # ── Sheet 12 : Price-Rating Correlation ──────────────────────────────
    corr = df["Price (INR)"].corr(df["Rating"])
    price_bins = pd.cut(df["Price (INR)"], bins=10)
    corr_df = (
        df.groupby(price_bins, observed=True)
        .agg(Orders=("Price (INR)", "count"),
             Avg_Rating=("Rating", "mean"),
             Avg_Price=("Price (INR)", "mean"))
        .round(3)
        .reset_index()
    )
    corr_df.columns = ["Price Range", "Orders", "Avg Rating", "Avg Price (INR)"]
    corr_df["Price Range"] = corr_df["Price Range"].astype(str)
    _build_sheet(
        wb, "12. Price-Rating",
        f"Price vs Rating Correlation  (Pearson r = {corr:.3f})",
        corr_df,
    )

    # ── Sheet 13 : Restaurant Frequency Tiers ────────────────────────────
    rest_df = (
        df.groupby("Restaurant Name")
        .agg(Orders=("Price (INR)", "count"),
             Revenue=("Price (INR)", "sum"),
             Avg_Rating=("Rating", "mean"),
             City=("City", "first"),
             State=("State", "first"))
        .round(2)
        .sort_values("Orders", ascending=False)
        .reset_index()
    )
    rest_df["Frequency Tier"] = pd.cut(
        rest_df["Orders"].rank(pct=True),
        bins=[0, 0.40, 0.80, 1.0],
        labels=["Low Volume (Bottom 40%)", "Medium Volume (40-80%)", "High Volume (Top 20%)"],
    )
    rest_df = rest_df[
        ["Restaurant Name", "City", "State", "Frequency Tier", "Orders", "Revenue", "Avg_Rating"]
    ]
    rest_df.columns = [
        "Restaurant", "City", "State", "Frequency Tier",
        "Orders", "Revenue (INR)", "Avg Rating"
    ]
    _build_sheet(
        wb, "13. Restaurant Frequency",
        "Restaurant Order Frequency Segmentation (Top 100)",
        rest_df.head(100),
    )

    # ── Output ────────────────────────────────────────────────────────────
    if output_path:
        wb.save(output_path)
        return output_path
    else:
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.read()


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Reading swiggy_data.xlsx …")
    raw_df = pd.read_excel("swiggy_data.xlsx")
    out_path = "swiggy_kpi_report.xlsx"
    generate_report(raw_df, output_path=out_path)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"Excel report saved: {out_path}  ({size_kb} KB, 13 sheets)")
