# 🍽️ Swiggy Sales Analysis - End-to-End Analytics Project

A comprehensive data analysis project on Swiggy's food delivery platform demonstrating **Python**, **statistical analysis**, **data visualization**, and **interactive dashboards**. 

## 📌 Overview

Analyzed 197,430 orders across multiple states/cities to identify revenue drivers, customer behavior patterns, and growth opportunities. Features both a **detailed Jupyter notebook** and an **interactive Streamlit dashboard** for business intelligence.

**Key Metrics:**
- ₹ Total Revenue Analysis
- 📊 197,430 Orders Analyzed  
- 🗺️ Multi-State Geographic Insights
- 📈 Time Series & Trend Analysis
- 🎯 Customer Segmentation (4 value tiers)
- 80/20 Pareto Analysis

---

## 🛠️ Tech Stack

| Component | Tools |
|-----------|-------|
| **Language** | Python 3.9+ |
| **Data** | Pandas, NumPy |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **Statistics** | SciPy, Statsmodels |
| **Dashboard** | Streamlit |
| **Environment** | Jupyter Notebook |

---

## 📊 Analysis Highlights

### Notebook Sections (13 Sections Total)

**Core Analysis (Sections 1-8):**

1. **Data Loading & EDA** - Data quality, missing values, duplicates, type validation
2. **KPI Dashboard** - Revenue, orders, AOV, ratings, satisfaction metrics
3. **Statistical Analysis** - Distributions, outliers, correlation, normality tests
4. **Time Series & Trends** - Monthly/daily patterns, growth rates, momentum
5. **Category & Geographic Analysis** - Food types, state/city breakdown, Pareto 80-20 rule
6. **Quarterly Performance** - Quarterly sales, orders, ratings comparison
7. **Customer Behavior & Segmentation** - RFM, value tiers (Budget→Luxury), ordering patterns
8. **Strategic Insights & Summary** - Key metrics, top performers, actionable insights

**Advanced Analytics (Sections 9-11):**

9. **Geographic Visualizations & Maps** - Bubble maps, city heatmaps, regional analysis
10. **Predictive Analytics & Forecasting** - Moving averages, trend smoothing, revenue projections
11. **Executive Summary & Action Items** - Consolidated findings & recommendations

**WOW Factors (Sections 12-13):**

12. **Executive Business Recommendations** 🎯
    - Top 3 states for marketing prioritization with ROI metrics
    - Optimal price bands (Budget→Luxury) with revenue-rating trade-offs
    - Customer tier strategies: Retention vs Acquisition by segment
    - Decision-oriented insights for C-suite stakeholders

13. **Predictive Forecasting with ARIMA** 📈
    - ARIMA(1,1,1) time series model with statistical validation
    - 3-month revenue forecast with 95% confidence intervals
    - Model metrics: AIC, BIC, R-squared, error rates
    - Actual vs predicted comparison with fallback moving average

---

### Interactive Dashboard (Streamlit - app.py)

**5 Analytics Tabs with 20+ Visualizations:**
- **Overview:** Food category mix, quarterly performance, daily patterns
- **Geographic:** State/city rankings, performance scatter plots
- **Segments:** Customer tiers, food preferences heatmap
- **Trends:** Monthly revenue with MA, growth rate analysis
- **Insights:** Pareto charts, correlation analysis, key statistics

**Interactive Features:**
- ✅ Date range filtering (dynamic across all charts)
- ✅ Multi-select state filters  
- ✅ Food category filtering
- ✅ Real-time KPI cards
- ✅ Hover tooltips & zoom capabilities

---

## 📁 Project Structure

```
Data_anlytics_project/
├── swiggy_sales_analysis.ipynb    # Full analysis notebook
│                                   # 13 sections, 60 cells
│                                   # Sections 1-8: Core Analysis
│                                   # Sections 9-11: Advanced Analytics
│                                   # Sections 12-13: WOW Factors
├── app.py                         # Streamlit dashboard (5 tabs, 20+ visualizations)
├── swiggy_data.xlsx               # Dataset (197,430 orders × 10 columns)
├── requirements.txt               # 11 dependencies (pandas, plotly, statsmodels...)
└── README.md                      # Documentation (this file)
```

---

## 🚀 Quick Start

### Option 1: Jupyter Notebook (Full Analysis)

```bash
# Install dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook swiggy_sales_analysis.ipynb
```

Run cells sequentially to explore all analysis sections.

### Option 2: Interactive Dashboard (Streamlit)

```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
python3 -m streamlit run app.py

# Open browser to: http://localhost:8501
```

**Dashboard Usage:**
- Use sidebar filters to explore data dynamically
- Click tabs to view different analytics sections
- Hover over charts for detailed tooltips
- Download visualizations using chart tools

---

## 💼 Skills Demonstrated

- ✅ **Data Analysis:** Pandas, NumPy, exploratory analysis
- ✅ **Statistical Methods:** Correlation, distribution, outlier detection
- ✅ **Data Visualization:** Interactive dashboards, storytelling
- ✅ **Time Series:** Trends, moving averages, ARIMA forecasting
- ✅ **Business Intelligence:** KPIs, segmentation, Pareto analysis, recommendations
- ✅ **Python Development:** Clean code, documentation, best practices
- ✅ **Predictive Modeling:** ARIMA forecasting, model validation
- ✅ **SQL Translation:** All analysis logic is database-translatable

---

## 🗄️ SQL-Ready Analysis (ATS & Data Engineering Bonus)

**Key Feature:** All analysis logic in this project can be directly translated to **SQL** for production pipelines.

### SQL-Equivalent Operations Used:

| Python (Pandas) | SQL Equivalent | Use Case |
|---|---|---|
| `groupby().agg()` | `GROUP BY` + aggregates | Revenue by state, city |
| `groupby().cumsum()` | Window Functions `SUM() OVER()` | Cumulative revenue, Pareto analysis |
| `merge()` on multiple keys | `JOIN ... ON` conditions | State-city hierarchies |
| `rolling()` | Window Functions `ROWS BETWEEN` | Moving averages, trends |
| `.rank()` / `.nlargest()` | `ROW_NUMBER()`, `RANK()` | Top N rankings |
| `.cut()` binning | `CASE WHEN` statements | Customer segmentation |
| Time-based grouping | `DATE_TRUNC()`, `EXTRACT()` | Monthly/quarterly rollups |

### Production-Ready Patterns Demonstrated:
```sql
-- Example: Pareto Analysis (80-20 Rule)
WITH city_revenue AS (
    SELECT City, SUM(price) as revenue
    FROM orders GROUP BY City
),
ranked_revenue AS (
    SELECT City, revenue,
           SUM(revenue) OVER (ORDER BY revenue DESC) as cumulative_revenue
    FROM city_revenue
),
total_revenue AS (
    SELECT SUM(revenue) as total FROM city_revenue
)
SELECT city, revenue,
       (cumulative_revenue / total * 100) as cumulative_pct
FROM ranked_revenue, total_revenue
WHERE cumulative_revenue <= (total * 0.8);
```

**Why This Matters:**
- 🎯 Shows understanding of **scalable data architecture**
- 🎯 Demonstrates **production-ready thinking**
- 🎯 Qualifies for **SQL + Python hybrid roles**
- 🎯 Broadens eligibility to **Data Engineering** positions


---

## � Contact & Links

**Mounusha Ram Metti**
- 📧 Email: mettti.mounu@gmail.com
- 💼 LinkedIn: linkedin.com/in/mounusha-ram-metti
- 🌐 Portfolio: https://mounushametti.vercel.app/
- 💻 GitHub: github.com/Mounusha25
