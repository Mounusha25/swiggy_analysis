# 🚀 Streamlit Dashboard Setup Guide

## Overview

An interactive Streamlit dashboard for real-time Swiggy sales analytics with dynamic filtering, KPI tracking, and multi-tab visualization.

---

## ✨ Dashboard Features

### 📊 Key Performance Indicators (KPIs)
- **Total Sales** - Cumulative revenue
- **Total Orders** - Number of transactions
- **Avg Order Value** - Mean transaction amount
- **Avg Rating** - Customer satisfaction score
- **Cities Covered** - Geographic reach

### 🎯 Interactive Filters
- **Date Range** - Select custom date periods
- **Food Category** - Filter by Veg/Non-Veg
- **State** - Choose specific states
- All filters work together in real-time

### 📈 Five Analytics Tabs

**Tab 1: Sales Trends**
- Monthly revenue line chart
- Daily sales pattern by day of week
- Trend analysis and seasonality

**Tab 2: Category Analysis**
- Revenue distribution (Veg vs Non-Veg pie chart)
- Orders count by food category
- Category performance metrics

**Tab 3: Geographic Insights**
- Top 15 states by revenue
- Top 10 cities by sales
- Geographic heatmap analysis

**Tab 4: Quarterly Performance**
- Quarterly revenue analysis
- Quarterly order counts
- Quarterly average ratings

**Tab 5: Customer Segments**
- Revenue by customer segments (Budget/Standard/Premium/Luxury)
- Order distribution across segments
- Segment statistics table with metrics

---

## 🛠️ Installation

### Step 1: Install Streamlit
```bash
pip install streamlit
# Or install all dependencies
pip install -r requirements.txt
```

### Step 2: Verify Installation
```bash
streamlit --version
```

---

## 🎮 Running the Dashboard

### From Command Line
```bash
# Navigate to project directory
cd /Users/mounusha/Downloads/Projects/Data_anlytics_project

# Run the Streamlit app
streamlit run streamlit_app.py
```

### Expected Output
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Access Dashboard
- Open browser to: **http://localhost:8501**
- Use the left sidebar to adjust filters
- Click tabs to explore different analyses

---

## 📁 File Structure

```
Data_anlytics_project/
├── streamlit_app.py          ← Dashboard application
├── swiggy_sales_analysis.ipynb
├── swiggy_data.xlsx          ← Required data file
├── requirements.txt
├── README.md
└── PROJECT_SUMMARY.md
```

---

## ⚙️ Configuration

### Customize Dashboard

**Change Page Title:**
```python
st.set_page_config(
    page_title="Your Title",
    page_icon="📊",
    layout="wide"
)
```

**Modify Colors:**
Edit color codes in Plotly figures:
```python
color_discrete_map={'Veg': '#2ecc71', 'Non-Veg': '#e74c3c'}
```

**Add More Filters:**
```python
new_filter = st.sidebar.multiselect("Filter Name:", options)
```

---

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Solution:**
```bash
pip install streamlit --upgrade
```

### Issue: "FileNotFoundError: swiggy_data.xlsx"
**Solution:**
- Ensure `swiggy_data.xlsx` is in the same directory as `streamlit_app.py`
- Use absolute path in code if needed

### Issue: Dashboard runs slowly
**Solution:**
- Use `@st.cache_data` decorator (already implemented)
- Reduce data size for testing
- Close other applications

### Issue: Filters not working
**Solution:**
- Check column names match your data
- Verify data types are correct
- Clear Streamlit cache: `streamlit cache clear`

---

## 🚀 Deployment Options

### 1. **Streamlit Cloud (Recommended - Free)**
```bash
# Create GitHub repo (already done)
# Connect to Streamlit Cloud at streamlit.io
# Select repo and deploy
```

### 2. **Heroku Deployment**
```bash
# Create Procfile and setup.sh
# Deploy using: git push heroku main
```

### 3. **AWS/Azure**
- Use EC2 or App Service
- Configure domain and SSL

### 4. **Local Server**
```bash
streamlit run streamlit_app.py --server.port 8501
```

---

## 📊 Dashboard Capabilities

### Real-Time Filtering
- Select date range → Updates all charts
- Choose food category → Filters relevant metrics
- Pick states → Shows state-specific analysis

### Interactive Charts
- **Hover** over data points for details
- **Click** legend items to toggle series
- **Zoom** and **pan** for detailed view
- **Download** as PNG

### Responsive Design
- Works on desktop, tablet, mobile
- Auto-adjusts column layout
- Touch-friendly interface

---

## 💡 Tips & Tricks

### Performance Optimization
```python
# Already implemented caching
@st.cache_data
def load_data():
    # Data loading
    return df
```

### Add Custom Styling
```python
st.markdown("""
<style>
    .custom-class {
        background-color: #f0f2f6;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)
```

### Add More Metrics
```python
with st.metric("New KPI", value, delta):
    # Your metric
```

---

## 🎓 Learning Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Plotly Charts:** https://plotly.com/python
- **Streamlit Gallery:** https://streamlit.io/gallery

---

## 📝 Next Steps

1. **Run Dashboard:** `streamlit run streamlit_app.py`
2. **Test Filters:** Verify all interactive elements work
3. **Customize:** Adjust colors, add more metrics
4. **Deploy:** Share dashboard with team/stakeholders
5. **Share Link:** Deploy to Streamlit Cloud for easy access

---

## 📞 Support

For issues or questions:
- Check Streamlit documentation
- Review GitHub repository
- Test with sample data
- Check browser console for errors

---

**🎉 Your interactive dashboard is ready to showcase your analytics skills!**
