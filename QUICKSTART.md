# ⚡ Quick Start Guide

## 🚀 Get Started in 2 Minutes

### Option 1: Run the Dashboard (Recommended)
```bash
# Navigate to project
cd /Users/mounusha/Downloads/Projects/Data_anlytics_project

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run streamlit_app.py
```

**Access:** http://localhost:8501

---

### Option 2: Run Jupyter Notebook
```bash
# Navigate to project
cd /Users/mounusha/Downloads/Projects/Data_anlytics_project

# Install dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook swiggy_sales_analysis.ipynb
```

---

## 📊 Dashboard Overview

### Five Tabs Available:

1. **📈 Sales Trends**
   - Monthly revenue line chart
   - Daily sales by weekday
   - Trend analysis

2. **🍴 Category Analysis**
   - Veg vs Non-Veg revenue split
   - Order counts by category
   - Category performance

3. **🗺️ Geographic Insights**
   - Top 15 states by revenue
   - Top 10 cities by sales
   - Geographic analysis

4. **📊 Quarterly Performance**
   - Quarterly sales comparison
   - Orders per quarter
   - Average ratings by quarter

5. **👥 Customer Segments**
   - Revenue by segment (Budget/Standard/Premium/Luxury)
   - Order distribution
   - Segment statistics table

---

## 🎯 Using Filters

**Left Sidebar Controls:**
- 📅 **Date Range:** Select custom date periods
- 🍴 **Food Category:** Choose Veg, Non-Veg, or both
- 🏘️ **State:** Select one or multiple states

**All filters work together** - apply multiple filters to drill down into data!

---

## 💡 Key Metrics Displayed

```
💰 Total Sales        → Total revenue in selected period
📦 Total Orders       → Number of orders
💵 Avg Order Value    → Mean order amount
⭐ Avg Rating         → Customer satisfaction (1-5)
🏙️  Cities Covered     → Geographic reach
```

---

## 📁 Project Files

```
Data_anlytics_project/
├── streamlit_app.py              ← 🎯 Run this for dashboard!
├── swiggy_sales_analysis.ipynb   ← 📊 Jupyter notebook
├── swiggy_data.xlsx              ← 📈 Dataset
├── requirements.txt              ← 📋 Dependencies
├── README.md                     ← 📖 Full documentation
├── DASHBOARD_GUIDE.md            ← 🎮 Dashboard help
└── PROJECT_SUMMARY.md            ← 📝 Project overview
```

---

## ⚙️ Requirements

- Python 3.8+
- pandas, numpy
- plotly, matplotlib, seaborn
- streamlit
- scipy, openpyxl

**Install all at once:**
```bash
pip install -r requirements.txt
```

---

## 🐛 Troubleshooting

### Dashboard won't start?
```bash
pip install --upgrade streamlit
streamlit run streamlit_app.py
```

### Data file not found?
- Ensure `swiggy_data.xlsx` is in the same folder
- Check file name spelling

### Slow dashboard?
- Data is cached automatically
- Clear cache: `streamlit cache clear`

---

## 📞 Next Steps

1. ✅ Run the dashboard: `streamlit run streamlit_app.py`
2. ✅ Try different filters
3. ✅ Export visualizations (click camera icon)
4. ✅ Share dashboard link with team
5. ✅ Customize colors/metrics as needed

---

## 🎓 Learn More

- 📖 [Full README](README.md)
- 🎮 [Dashboard Guide](DASHBOARD_GUIDE.md)
- 📊 [Project Summary](PROJECT_SUMMARY.md)
- 🌐 [GitHub Repository](https://github.com/Mounusha25/swiggy_analysis)

---

**🎉 You're all set! Start exploring your data!**
