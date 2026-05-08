"""
sql_pipeline.py
---------------
Loads Swiggy order data from Excel into a SQLite database and exposes
pre-built SQL analytics queries.

Standalone usage:
    python3 sql_pipeline.py

Imported by app.py for the SQL Analytics tab.
"""

import sqlite3
import os
import pandas as pd

DB_PATH = "swiggy.db"
EXCEL_PATH = "swiggy_data.xlsx"


def setup_database(excel_path: str = EXCEL_PATH, db_path: str = DB_PATH) -> str:
    """
    Read swiggy_data.xlsx and load it into a SQLite database as the 'orders' table.
    Adds derived columns (Year_Month, Quarter, DayName, DayOfWeek) before inserting.
    Returns the path to the created database file.
    """
    df = pd.read_excel(excel_path)

    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Year_Month"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["DayName"] = df["Order Date"].dt.day_name()
    df["DayOfWeek"] = df["Order Date"].dt.dayofweek  # 0=Monday
    df["Order Date"] = df["Order Date"].astype(str)  # SQLite-friendly

    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS orders")
    conn.commit()
    df.to_sql("orders", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

    return db_path


def run_query(sql: str, db_path: str = DB_PATH) -> pd.DataFrame:
    """Execute a SQL query against the Swiggy SQLite database and return a DataFrame."""
    conn = sqlite3.connect(db_path)
    result = pd.read_sql_query(sql, conn)
    conn.close()
    return result


# ---------------------------------------------------------------------------
# Pre-built analytics queries
# ---------------------------------------------------------------------------
QUERIES = {
    "Monthly Revenue & Seasonality": {
        "sql": """\
SELECT
    Year_Month                           AS "Month",
    COUNT(*)                             AS "Orders",
    ROUND(SUM("Price (INR)"), 2)         AS "Revenue (INR)",
    ROUND(AVG("Price (INR)"), 2)         AS "Avg Order Value (INR)",
    ROUND(AVG(Rating), 3)                AS "Avg Rating"
FROM orders
GROUP BY Year_Month
ORDER BY Year_Month;""",
        "description": (
            "Tracks revenue and order volume month over month to identify "
            "seasonality patterns and improve sales forecasting."
        ),
    },

    "Revenue by State": {
        "sql": """\
SELECT
    State,
    COUNT(*)                             AS "Orders",
    ROUND(SUM("Price (INR)"), 2)         AS "Revenue (INR)",
    ROUND(AVG("Price (INR)"), 2)         AS "Avg Order Value (INR)",
    ROUND(AVG(Rating), 3)                AS "Avg Rating"
FROM orders
GROUP BY State
ORDER BY "Revenue (INR)" DESC
LIMIT 15;""",
        "description": (
            "Ranks states by total revenue to identify top-performing geographic "
            "markets for targeted marketing investment."
        ),
    },

    "Revenue by Food Category": {
        "sql": """\
SELECT
    Category                             AS "Food Category",
    COUNT(*)                             AS "Orders",
    ROUND(SUM("Price (INR)"), 2)         AS "Revenue (INR)",
    ROUND(AVG("Price (INR)"), 2)         AS "Avg Order Value (INR)",
    ROUND(AVG(Rating), 3)                AS "Avg Rating"
FROM orders
GROUP BY Category
ORDER BY "Revenue (INR)" DESC
LIMIT 20;""",
        "description": (
            "Breaks down revenue by cuisine category to reveal high-value food "
            "segments and guide menu strategy."
        ),
    },

    "Quarterly Performance": {
        "sql": """\
SELECT
    Quarter,
    COUNT(*)                             AS "Orders",
    ROUND(SUM("Price (INR)"), 2)         AS "Revenue (INR)",
    ROUND(AVG("Price (INR)"), 2)         AS "Avg Order Value (INR)",
    ROUND(AVG(Rating), 3)                AS "Avg Rating"
FROM orders
GROUP BY Quarter
ORDER BY Quarter;""",
        "description": (
            "Aggregates sales by quarter for executive-level period-over-period "
            "comparison and seasonal planning."
        ),
    },

    "Top 20 Dishes by Revenue": {
        "sql": """\
SELECT
    "Dish Name"                          AS "Dish",
    COUNT(*)                             AS "Orders",
    ROUND(SUM("Price (INR)"), 2)         AS "Revenue (INR)",
    ROUND(AVG("Price (INR)"), 2)         AS "Avg Price (INR)",
    ROUND(AVG(Rating), 2)                AS "Avg Rating"
FROM orders
GROUP BY "Dish Name"
ORDER BY "Revenue (INR)" DESC
LIMIT 20;""",
        "description": (
            "Identifies highest-revenue dishes to inform menu optimisation, "
            "promotions, and restaurant partnership decisions."
        ),
    },

    "Top 20 Restaurants by Revenue": {
        "sql": """\
SELECT
    "Restaurant Name"                    AS "Restaurant",
    City,
    State,
    COUNT(*)                             AS "Orders",
    ROUND(SUM("Price (INR)"), 2)         AS "Revenue (INR)",
    ROUND(AVG(Rating), 2)                AS "Avg Rating"
FROM orders
GROUP BY "Restaurant Name", City, State
ORDER BY "Revenue (INR)" DESC
LIMIT 20;""",
        "description": (
            "Highlights top-performing restaurant partners by revenue for "
            "strategic account management and co-marketing opportunities."
        ),
    },

    "Day of Week Sales Pattern": {
        "sql": """\
SELECT
    DayName                              AS "Day",
    COUNT(*)                             AS "Orders",
    ROUND(SUM("Price (INR)"), 2)         AS "Revenue (INR)",
    ROUND(AVG("Price (INR)"), 2)         AS "Avg Order Value (INR)"
FROM orders
GROUP BY DayName, DayOfWeek
ORDER BY DayOfWeek;""",
        "description": (
            "Reveals weekly seasonality to optimise staffing, promotions, "
            "and delivery capacity by day of week."
        ),
    },

    "Customer Basket Segmentation": {
        "sql": """\
SELECT
    CASE
        WHEN "Price (INR)" <= 200              THEN 'Budget (<=200)'
        WHEN "Price (INR)" <= 500              THEN 'Standard (201-500)'
        WHEN "Price (INR)" <= 1000             THEN 'Premium (501-1000)'
        ELSE                                        'Luxury (>1000)'
    END                                      AS "Segment",
    COUNT(*)                                 AS "Orders",
    ROUND(SUM("Price (INR)"), 2)             AS "Revenue (INR)",
    ROUND(AVG("Price (INR)"), 2)             AS "Avg Order Value (INR)",
    ROUND(AVG(Rating), 2)                    AS "Avg Rating"
FROM orders
GROUP BY Segment
ORDER BY MIN("Price (INR)");""",
        "description": (
            "Segments orders by basket value (Budget / Standard / Premium / Luxury) "
            "to identify high-value customer tiers for retention campaigns."
        ),
    },

    "Restaurant Frequency Tiers": {
        "sql": """\
SELECT
    Tier                                 AS "Frequency Tier",
    COUNT(*)                             AS "Restaurants",
    SUM(Orders)                          AS "Total Orders",
    ROUND(SUM(Revenue), 2)               AS "Total Revenue (INR)",
    ROUND(AVG(Avg_Rating), 3)            AS "Avg Rating"
FROM (
    SELECT
        "Restaurant Name",
        COUNT(*)                         AS Orders,
        SUM("Price (INR)")               AS Revenue,
        AVG(Rating)                      AS Avg_Rating,
        CASE
            WHEN PERCENT_RANK() OVER (ORDER BY COUNT(*)) >= 0.80
                                         THEN 'High Volume (Top 20%)'
            WHEN PERCENT_RANK() OVER (ORDER BY COUNT(*)) >= 0.40
                                         THEN 'Medium Volume (40-80%)'
            ELSE                              'Low Volume (Bottom 40%)'
        END                              AS Tier
    FROM orders
    GROUP BY "Restaurant Name"
)
GROUP BY Tier
ORDER BY MIN(Orders) DESC;""",
        "description": (
            "Classifies restaurants by order volume into High / Medium / Low tiers "
            "as a proxy for purchase frequency segmentation."
        ),
    },

    "Pareto: Cities Driving 80% Revenue": {
        "sql": """\
WITH city_rev AS (
    SELECT
        City,
        ROUND(SUM("Price (INR)"), 2)     AS Revenue
    FROM orders
    GROUP BY City
    ORDER BY Revenue DESC
),
cumulative AS (
    SELECT
        City,
        Revenue,
        ROUND(
            SUM(Revenue) OVER (ORDER BY Revenue DESC) /
            SUM(Revenue) OVER () * 100
        , 2)                             AS "Cumulative Revenue %"
    FROM city_rev
)
SELECT *
FROM cumulative
WHERE "Cumulative Revenue %" <= 80
ORDER BY Revenue DESC;""",
        "description": (
            "Identifies the minimum set of cities that together generate 80% of "
            "total revenue (Pareto / 80-20 rule)."
        ),
    },
}


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Setting up SQLite database from swiggy_data.xlsx …")
    db = setup_database()
    print(f"Database created: {db} ({os.path.getsize(db):,} bytes)\n")

    for name, info in QUERIES.items():
        print(f"{'=' * 65}")
        print(f"Query : {name}")
        print(f"Desc  : {info['description']}")
        print(f"SQL   :\n{info['sql']}")
        df_result = run_query(info["sql"], db)
        print(f"Result ({len(df_result)} rows):")
        print(df_result.to_string(index=False))
        print()

    print("Done. All queries executed successfully.")
