# 🍽️ Swiggy Sales Analysis - Advanced Analytics Project

## 📌 Project Overview

A comprehensive end-to-end data analysis project analyzing Swiggy's food delivery platform data to uncover revenue drivers, customer behavior patterns, and strategic business insights. This project demonstrates proficiency in **Python**, **statistical analysis**, **data visualization**, and **business intelligence** - skills essential for Analytics roles at top tech companies.

---

## 🎯 Business Problem

**Objective:** Analyze Swiggy's sales data to identify growth opportunities, optimize geographic expansion, understand customer preferences, and provide data-driven recommendations to stakeholders.

**Key Questions:**
- What are the primary revenue drivers?
- Which geographic markets show the highest potential?
- How can we optimize customer segmentation for targeted marketing?
- What are the growth trends and future projections?

---

## 🛠️ Technical Stack

| Category | Technologies |
|----------|-------------|
| **Language** | Python 3.x |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **Statistical Analysis** | SciPy, Statsmodels |
| **Dashboard** | Streamlit |
| **Environment** | Jupyter Notebook |
| **Deployment** | Streamlit Cloud, GitHub |

---

## 📊 Analysis Framework

### 1. **Exploratory Data Analysis (EDA)**
- Data quality assessment & missing value analysis
- Statistical summary and distribution analysis
- Outlier detection using IQR method

### 2. **Business Metrics & KPIs**
- Total Revenue & Order Volume
- Average Order Value (AOV)
- Customer Satisfaction (Rating Analysis)
- Month-over-Month Growth Rate

### 3. **Advanced Statistical Analysis**
- **Distribution Analysis:** Normality testing, Q-Q plots, skewness/kurtosis
- **Correlation Analysis:** Heatmaps, scatter plots with regression lines
- **Outlier Detection:** Box plots, IQR-based identification

### 4. **Time Series Analysis**
- **Trend Analysis:** Monthly and daily sales patterns
- **Growth Metrics:** MoM growth rate, cumulative revenue
- **Forecasting:** Moving averages (3-month, 6-month)

### 5. **Geographic & Category Analysis**
- Revenue distribution by state and city
- Top 5 cities performance analysis
- Food category segmentation (Veg vs Non-Veg)
- **Pareto Analysis:** 80-20 rule for revenue concentration

### 6. **Customer Behavior Analytics**
- **RFM Segmentation:** Value-based customer segments
- **Cohort Analysis:** Budget, Standard, Premium, Luxury tiers
- Peak ordering hours analysis (when data available)

### 7. **Predictive Analytics**
- Simple moving average forecasting
- Revenue trend projections
- Growth rate predictions

### 8. **Strategic Recommendations**
- Data-driven business insights
- Actionable recommendations for stakeholders
- Executive summary with KPIs

### 9. **Interactive Dashboard (NEW)**
- **Real-time KPI Tracking:** Total sales, orders, AOV, ratings, cities
- **Dynamic Filtering:** Date range, food category, state-level filtering
- **5 Analytics Tabs:**
  - Sales Trends (Monthly & Daily patterns)
  - Category Analysis (Veg vs Non-Veg performance)
  - Geographic Insights (State & city-level breakdown)
  - Quarterly Performance (Multi-metric analysis)
  - Customer Segmentation (Budget to Luxury tiers)
- **Interactive Visualizations:** Hover, zoom, download capabilities
- **Responsive Design:** Works on desktop, tablet, mobile
- **Built with:** Streamlit + Plotly

---

## 📈 Key Insights & Findings

### Revenue Performance
- ✅ Identified **top 20% cities generating 80% revenue** (Pareto principle)
- ✅ Tracked **month-over-month growth trends** with visualization
- ✅ Analyzed **quarterly performance** across multiple metrics

### Customer Segmentation
- ✅ Segmented customers into **4 value tiers** (Budget to Luxury)
- ✅ Discovered **premium segment shows higher ratings** but lower volume
- ✅ Identified **revenue concentration** patterns

### Geographic Insights
- ✅ Mapped **top-performing states and cities**
- ✅ Identified **expansion opportunities** in tier-2 cities
- ✅ Analyzed **regional food preferences**

### Statistical Discoveries
- ✅ **Price-Rating correlation analysis** revealed weak relationship
- ✅ **Outlier detection** identified high-value orders (opportunities)
- ✅ **Distribution analysis** showed right-skewed pricing patterns

---

## 📁 Project Structure

```
Data_anlytics_project/
│
├── swiggy_sales_analysis.ipynb    # Main analysis notebook
├── swiggy_data.xlsx                # Dataset (Excel format)
├── README.md                       # Project documentation (this file)
└── requirements.txt                # Python dependencies
```

---

## 🚀 How to Run

### Prerequisites
```bash
# Install Python 3.8+
# Install Jupyter Notebook
pip install jupyter
```

### Installation
```bash
# Clone or download the project
cd Data_anlytics_project

# Install required packages
pip install -r requirements.txt

# Launch Jupyter Notebook
jupyter notebook swiggy_sales_analysis.ipynb
```

### 🎯 Running the Interactive Dashboard

```bash
# Install Streamlit if not already installed
pip install streamlit

# Run the dashboard
streamlit run streamlit_app.py

# Access at: http://localhost:8501
```

**Dashboard Features:**
- ✅ Real-time KPI metrics
- ✅ Interactive filters (date, category, state)
- ✅ 5 analytics tabs with 15+ visualizations
- ✅ Customer segmentation analysis
- ✅ Responsive design for all devices

📖 See [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) for detailed setup and usage instructions.
````

### Running the Analysis
1. Open `swiggy_sales_analysis.ipynb`
2. Run cells sequentially (Cell → Run All)
3. View interactive visualizations and insights
4. Export results as needed

---

## 📊 Sample Visualizations

The notebook includes:
- 📈 **Interactive Plotly charts** for dynamic exploration
- 📊 **Statistical plots** (histograms, box plots, Q-Q plots)
- 🗺️ **Geographic heatmaps** and bar charts
- 📉 **Time series trends** with moving averages
- 🥧 **Pie charts** for segmentation analysis
- 📐 **Correlation matrices** with heatmaps

---

## 💼 Skills Demonstrated

### Technical Skills
- ✅ **Python Programming:** Advanced Pandas/NumPy operations
- ✅ **Data Wrangling:** Cleaning, transformation, feature engineering
- ✅ **Statistical Analysis:** Hypothesis testing, correlation, distribution analysis
- ✅ **Data Visualization:** Interactive dashboards, storytelling with data
- ✅ **Time Series:** Trend analysis, forecasting, seasonality detection
- ✅ **Business Analytics:** KPI tracking, RFM, Pareto analysis

### Business Skills
- ✅ **Strategic Thinking:** Translating data into actionable insights
- ✅ **Stakeholder Communication:** Executive summaries, recommendations
- ✅ **Problem Solving:** Root cause analysis, optimization strategies
- ✅ **Domain Knowledge:** E-commerce, food delivery metrics


---

## 📝 Future Enhancements

- [ ] **A/B Testing Framework:** Statistical significance testing
- [ ] **Machine Learning:** Predictive models for churn, LTV
- [ ] **Cohort Analysis:** Retention curves, customer lifetime value
- [ ] **Advanced Forecasting:** ARIMA, Prophet models
- [ ] **Dashboard:** Interactive Streamlit/Dash app
- [ ] **SQL Integration:** Database queries, ETL pipelines

---

## 👤 Author

**Mounusha Ram Metti**
- 📧 Email: mettti.mounu@gmail.com
- 💼 LinkedIn: linkedin.com/in/mounusha-ram-metti
- 🌐 Portfolio: https://mounushametti.vercel.app/
- 💻 GitHub: github.com/Mounusha25

---

## 📄 License

This project is created for portfolio and educational purposes.

---

## 🙏 Acknowledgments

- Dataset: Swiggy sales data (sample/public dataset)
- Tools: Python ecosystem, Jupyter, Plotly
- Inspiration: Real-world analytics problems at tech companies

---

**⭐ If you find this project helpful, please star it!**
