import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from sklearn.preprocessing import MinMaxScaler
from sql_pipeline import setup_database, QUERIES, run_query
from generate_excel_report import generate_report
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================
st.set_page_config(
    page_title="Swiggy Market Intelligence Engine",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            color: #FF6B35;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2D3142;
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #FF6B35;
            padding-bottom: 0.5rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 0.5rem;
            color: white;
            text-align: center;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def load_data():
    df = pd.read_excel('swiggy_data.xlsx')
    
    # Data preprocessing
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Year-Month"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
    df["DayName"] = df["Order Date"].dt.day_name()
    df["DayOfWeek"] = df["Order Date"].dt.dayofweek

    # Synthetic Order Hour — modelled distribution (lunch + dinner peaks)
    rng = np.random.default_rng(42)
    hour_probs = np.array(
        [0.005, 0.005, 0.005, 0.005, 0.005, 0.005,   # 00-05 late night
         0.020, 0.030, 0.040,                          # 06-08 morning
         0.040, 0.060,                                 # 09-10 brunch
         0.100, 0.120, 0.100,                          # 11-13 lunch peak
         0.050, 0.040, 0.030,                          # 14-16 afternoon
         0.050, 0.060,                                 # 17-18 early evening
         0.120, 0.120, 0.100, 0.080,                   # 19-22 dinner peak
         0.040]                                        # 23    night
    )
    hour_probs = hour_probs / hour_probs.sum()
    df["Order Hour"] = rng.choice(24, size=len(df), p=hour_probs)
    df["Time Slot"] = pd.cut(
        df["Order Hour"],
        bins=[-1, 5, 10, 14, 17, 22, 23],
        labels=["Late Night", "Morning", "Lunch", "Afternoon", "Dinner", "Night"],
    )

    # Food category classification
    non_veg_keywords = ['chicken', 'mutton', 'fish', 'egg', 'prawn', 'meat', 'biryani', 'kebab', 'seafood', "non-veg", "non veg", "kabab"]
    df["Food Category"] = np.where(df['Dish Name'].str.lower().str.contains('|'.join(non_veg_keywords), na=False), 'Non-Veg', 'Veg')
    
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ Error: 'swiggy_data.xlsx' not found in the current directory. Please ensure the dataset is present.")
    st.stop()

# ============================================================================
# HEADER
# ============================================================================
st.markdown('<h1 class="main-header">🍽️ Swiggy Market Intelligence Engine</h1>', unsafe_allow_html=True)
st.markdown("**Decision-support analytics for Swiggy's growth, expansion, and restaurant strategy**", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================
st.sidebar.markdown("## 🔍 Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range:",
    value=(df["Order Date"].min().date(), df["Order Date"].max().date()),
    min_value=df["Order Date"].min().date(),
    max_value=df["Order Date"].max().date()
)

# State filter
all_states = sorted(df['State'].unique())
selected_states = st.sidebar.multiselect("Select States:", all_states, default=all_states[:5])

# Food category filter
food_categories = ['Both', 'Veg', 'Non-Veg']
selected_food = st.sidebar.selectbox("Food Category:", food_categories, index=0)

# Apply filters
df_filtered = df[
    (df["Order Date"].dt.date >= date_range[0]) &
    (df["Order Date"].dt.date <= date_range[1]) &
    (df['State'].isin(selected_states))
]

if selected_food != 'Both':
    df_filtered = df_filtered[df_filtered['Food Category'] == selected_food]

# About
st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ About this project"):
    st.markdown("""
    **Swiggy Market Intelligence Engine** turns 197K+ food delivery orders into actionable strategy.

    **3 Proprietary Frameworks:**
    - 🍽️ Menu Intelligence Matrix (BCG-style)
    - 🏙️ City Expansion Opportunity Index
    - 🏥 Restaurant Health Score

    Built with Python • Pandas • Plotly • SQLite • Streamlit
    """)

# Excel export
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Export Report")
if st.sidebar.button("Generate Excel KPI Report"):
    with st.spinner("Building 13-sheet Excel report…"):
        st.session_state["excel_bytes"] = generate_report(df_filtered)
if st.session_state.get("excel_bytes"):
    st.sidebar.download_button(
        label="📥 Download Excel Report",
        data=st.session_state["excel_bytes"],
        file_name="swiggy_kpi_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# ============================================================================
# KEY METRICS
# ============================================================================
st.markdown('<h2 class="sub-header">📊 Key Performance Indicators</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = df_filtered['Price (INR)'].sum()
    st.metric("Total Revenue", f"₹{total_sales:,.0f}", delta=None)

with col2:
    total_orders = len(df_filtered)
    st.metric("Total Orders", f"{total_orders:,}", delta=None)

with col3:
    avg_order_value = df_filtered['Price (INR)'].mean()
    st.metric("Avg Order Value", f"₹{avg_order_value:,.0f}", delta=None)

with col4:
    avg_rating = df_filtered['Rating'].mean()
    st.metric("Avg Rating", f"{avg_rating:.2f} / 5.0", delta=None)

# ============================================================================
# TABS LAYOUT
# ============================================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    ["📈 Overview", "🗺️ Geographic", "🎯 Segments", "📉 Trends", "💡 Insights", "🗄️ SQL Pipeline", "📍 Expansion Strategy"]
)

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================
with tab1:
    st.markdown('<h3 class="sub-header">Revenue Distribution</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Food category pie chart
        food_revenue = df_filtered.groupby("Food Category")['Price (INR)'].sum().reset_index()
        fig_food = px.pie(
            food_revenue,
            names='Food Category',
            values='Price (INR)',
            title='Revenue by Food Type',
            hole=0.4,
            color_discrete_map={'Veg': '#2ecc71', 'Non-Veg': '#e74c3c'}
        )
        fig_food.update_traces(textinfo='label+percent')
        st.plotly_chart(fig_food, width="stretch")
    
    with col2:
        # Quarterly performance
        quarterly = df_filtered.groupby('Quarter', as_index=False).agg(
            Sales=('Price (INR)', 'sum'),
            Orders=('Order Date', 'count'),
            Avg_Rating=('Rating', 'mean')
        ).sort_values('Quarter')
        
        fig_quarterly = go.Figure()
        fig_quarterly.add_trace(go.Bar(
            x=quarterly['Quarter'],
            y=quarterly['Sales'],
            name='Revenue (₹)',
            marker_color='#667eea'
        ))
        fig_quarterly.update_layout(
            title='Quarterly Performance',
            xaxis_title='Quarter',
            yaxis_title='Revenue (₹)',
            hovermode='x unified'
        )
        st.plotly_chart(fig_quarterly, width="stretch")
    
    st.markdown('<h3 class="sub-header">Daily Sales Pattern</h3>', unsafe_allow_html=True)
    
    daily_revenue = (df_filtered.groupby("DayName")['Price (INR)'].sum()
                    .reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']))
    
    fig_daily = px.bar(
        x=daily_revenue.index,
        y=daily_revenue.values,
        title='Sales by Day of Week',
        labels={'x': 'Day', 'y': 'Revenue (₹)'},
        color=daily_revenue.values,
        color_continuous_scale='Viridis'
    )
    fig_daily.update_layout(showlegend=False)
    st.plotly_chart(fig_daily, width="stretch")

# ============================================================================
# TAB 2: GEOGRAPHIC
# ============================================================================
with tab2:
    st.markdown('<h3 class="sub-header">Geographic Performance</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        # Top states by revenue
        state_revenue = df_filtered.groupby("State", as_index=False)['Price (INR)'].sum().sort_values('Price (INR)', ascending=True).tail(15)
        
        fig_state = px.bar(
            state_revenue,
            x="Price (INR)",
            y="State",
            title="Top 15 States by Revenue",
            orientation='h',
            color="Price (INR)",
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_state, width="stretch")
    
    with col2:
        # Top cities
        city_revenue = (df_filtered.groupby("City")["Price (INR)"]
                       .sum()
                       .nlargest(10)
                       .sort_values()
                       .reset_index())
        
        fig_city = px.bar(
            city_revenue,
            x="Price (INR)",
            y="City",
            title="Top 10 Cities by Revenue",
            orientation='h',
            color="Price (INR)",
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_city, width="stretch")
    
    st.markdown('<h3 class="sub-header">State Analysis</h3>', unsafe_allow_html=True)
    
    state_analysis = df_filtered.groupby('State').agg({
        'Price (INR)': ['sum', 'count', 'mean'],
        'Rating': 'mean'
    }).round(2)
    state_analysis.columns = ['Total Revenue', 'Orders', 'Avg Price', 'Avg Rating']
    state_analysis = state_analysis.sort_values('Total Revenue', ascending=False).head(10)
    
    fig_state_scatter = px.scatter(
        state_analysis.reset_index(),
        x='Avg Rating',
        y='Total Revenue',
        size='Orders',
        color='Avg Rating',
        hover_name='State',
        title='State Performance: Revenue vs Ratings',
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig_state_scatter, width="stretch")

# ============================================================================
# TAB 3: SEGMENTS
# ============================================================================
with tab3:
    st.markdown('<h3 class="sub-header">Customer Segmentation</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Order value segments
        df_filtered['Value_Segment'] = pd.cut(
            df_filtered['Price (INR)'],
            bins=[0, 200, 500, 1000, float('inf')],
            labels=['Budget', 'Standard', 'Premium', 'Luxury']
        )
        
        segment_analysis = df_filtered.groupby('Value_Segment').agg({
            'Price (INR)': ['sum', 'count']
        }).round(0)
        segment_analysis.columns = ['Revenue', 'Orders']
        segment_analysis = segment_analysis.reset_index()
        
        fig_segment_pie = px.pie(
            segment_analysis,
            names='Value_Segment',
            values='Revenue',
            title='Revenue by Order Value Segment',
            hole=0.4
        )
        st.plotly_chart(fig_segment_pie, width="stretch")
    
    with col2:
        fig_segment_orders = px.bar(
            segment_analysis,
            x='Value_Segment',
            y='Orders',
            title='Order Count by Segment',
            color='Orders',
            color_continuous_scale='Plasma'
        )
        st.plotly_chart(fig_segment_orders, width="stretch")
    
    st.markdown('<h3 class="sub-header">Food Preference by State</h3>', unsafe_allow_html=True)
    
    # Food type heatmap
    state_food = df_filtered.groupby(['State', 'Food Category']).agg({
        'Price (INR)': 'count'
    }).reset_index()
    state_food.columns = ['State', 'Food Category', 'Orders']
    
    top_states = df_filtered['State'].value_counts().head(10).index.tolist()
    state_food_top = state_food[state_food['State'].isin(top_states)]
    
    heatmap_data = state_food_top.pivot_table(
        index='State',
        columns='Food Category',
        values='Orders',
        fill_value=0
    )
    
    fig_heatmap = px.imshow(
        heatmap_data,
        labels=dict(x="Food Category", y="State", color="Orders"),
        title="Food Type Preference by State",
        color_continuous_scale='YlOrRd'
    )
    st.plotly_chart(fig_heatmap, width="stretch")

    # ── Restaurant Frequency Segmentation ──────────────────────────────────
    st.markdown('<h3 class="sub-header">Purchase Frequency Segmentation</h3>', unsafe_allow_html=True)
    st.caption("Restaurants are classified into frequency tiers by order volume — used as a proxy for customer visit frequency.")

    rest_orders = df_filtered.groupby("Restaurant Name")["Price (INR)"].count().reset_index()
    rest_orders.columns = ["Restaurant", "Orders"]
    rest_orders["Frequency Tier"] = pd.cut(
        rest_orders["Orders"].rank(pct=True),
        bins=[0, 0.40, 0.80, 1.0],
        labels=["Low Volume", "Medium Volume", "High Volume"],
    )

    freq_summary = rest_orders.groupby("Frequency Tier", observed=True).agg(
        Restaurants=("Restaurant", "count"),
        Total_Orders=("Orders", "sum"),
    ).reset_index()
    freq_summary.columns = ["Frequency Tier", "Restaurants", "Total Orders"]

    col1, col2 = st.columns(2)
    with col1:
        fig_freq = px.bar(
            freq_summary,
            x="Frequency Tier",
            y="Total Orders",
            title="Orders by Restaurant Frequency Tier",
            color="Frequency Tier",
            color_discrete_map={
                "Low Volume": "#e74c3c",
                "Medium Volume": "#f39c12",
                "High Volume": "#2ecc71",
            },
            text="Total Orders",
        )
        fig_freq.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_freq.update_layout(showlegend=False)
        st.plotly_chart(fig_freq, width="stretch")
    with col2:
        fig_freq_r = px.bar(
            freq_summary,
            x="Frequency Tier",
            y="Restaurants",
            title="Restaurant Count by Frequency Tier",
            color="Frequency Tier",
            color_discrete_map={
                "Low Volume": "#e74c3c",
                "Medium Volume": "#f39c12",
                "High Volume": "#2ecc71",
            },
            text="Restaurants",
        )
        fig_freq_r.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_freq_r.update_layout(showlegend=False)
        st.plotly_chart(fig_freq_r, width="stretch")

    # ── Time of Day Analysis ──────────────────────────────────────────────
    st.markdown('<h3 class="sub-header">Time of Day Order Patterns</h3>', unsafe_allow_html=True)
    st.caption("Order hours are modelled from a realistic delivery distribution (lunch + dinner peaks).")

    slot_order = ["Morning", "Lunch", "Afternoon", "Dinner", "Night", "Late Night"]
    tod = (
        df_filtered.groupby("Time Slot", observed=True)["Price (INR)"]
        .count()
        .reindex(slot_order)
        .reset_index()
    )
    tod.columns = ["Time Slot", "Orders"]

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
        fig_tod.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_tod.update_layout(showlegend=False)
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

    # Day × Time Slot heatmap
    day_slot = df_filtered.groupby(
        ["DayName", "Time Slot"], observed=True
    )["Price (INR)"].count().reset_index()
    day_slot.columns = ["Day", "Time Slot", "Orders"]
    day_order_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot_ds = day_slot.pivot_table(index="Day", columns="Time Slot", values="Orders", fill_value=0)
    pivot_ds = pivot_ds.reindex(day_order_list)
    pivot_ds = pivot_ds.reindex(columns=[c for c in slot_order if c in pivot_ds.columns])
    fig_ds_heatmap = px.imshow(
        pivot_ds,
        labels=dict(x="Time Slot", y="Day", color="Orders"),
        title="Order Density: Day of Week × Time Slot",
        color_continuous_scale="YlOrRd",
        aspect="auto",
    )
    st.plotly_chart(fig_ds_heatmap, width="stretch")

# ============================================================================
# TAB 4: TRENDS
# ============================================================================
with tab4:
    st.markdown('<h3 class="sub-header">Time Series Analysis</h3>', unsafe_allow_html=True)
    
    monthly_revenue = df_filtered.groupby("Year-Month")["Price (INR)"].sum().reset_index().sort_values('Year-Month')
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Monthly trend with moving average
        monthly_revenue['MA_3'] = monthly_revenue['Price (INR)'].rolling(window=3).mean()
        
        fig_monthly = go.Figure()
        
        fig_monthly.add_trace(go.Scatter(
            x=monthly_revenue['Year-Month'],
            y=monthly_revenue['Price (INR)'],
            mode='lines+markers',
            name='Actual Revenue',
            line=dict(color='lightblue', width=1),
            fill='tozeroy'
        ))
        
        fig_monthly.add_trace(go.Scatter(
            x=monthly_revenue['Year-Month'],
            y=monthly_revenue['MA_3'],
            mode='lines',
            name='3-Month MA',
            line=dict(color='red', width=2)
        ))
        
        fig_monthly.update_layout(
            title='Monthly Revenue Trend',
            xaxis_title='Month',
            yaxis_title='Revenue (₹)',
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_monthly, width="stretch")
    
    with col2:
        if len(monthly_revenue) > 1:
            mom_growth = ((monthly_revenue['Price (INR)'].iloc[-1] - monthly_revenue['Price (INR)'].iloc[-2]) / 
                         monthly_revenue['Price (INR)'].iloc[-2] * 100)
            avg_growth = monthly_revenue['Price (INR)'].pct_change().mean() * 100
            
            st.metric("Last Month MoM Growth", f"{mom_growth:.2f}%")
            st.metric("Avg Monthly Growth", f"{avg_growth:.2f}%")
    
    st.markdown('<h3 class="sub-header">Growth Rate Analysis</h3>', unsafe_allow_html=True)
    
    monthly_revenue['MoM_Growth'] = monthly_revenue['Price (INR)'].pct_change() * 100
    
    fig_growth = px.bar(
        monthly_revenue.dropna(),
        x='Year-Month',
        y='MoM_Growth',
        title='Month-over-Month Growth Rate',
        color='MoM_Growth',
        color_continuous_scale=['red', 'yellow', 'green'],
        color_continuous_midpoint=0
    )
    st.plotly_chart(fig_growth, width="stretch")

# ============================================================================
# TAB 5: INSIGHTS
# ============================================================================
with tab5:
    st.markdown('<h3 class="sub-header">Strategic Insights</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📌 Pareto Analysis (80-20 Rule)")
        city_revenue = df_filtered.groupby('City')['Price (INR)'].sum().sort_values(ascending=False).reset_index()
        city_revenue['Cumulative_Percentage'] = (city_revenue['Price (INR)'].cumsum() / city_revenue['Price (INR)'].sum()) * 100
        city_revenue['City_Rank'] = range(1, len(city_revenue) + 1)
        
        top_80_cities = city_revenue[city_revenue['Cumulative_Percentage'] <= 80]
        
        st.markdown(f"""
        - **Top {len(top_80_cities)} cities** generate **80% of revenue**
        - **Total cities:** {len(city_revenue)}
        - **Concentration ratio:** {len(top_80_cities)/len(city_revenue)*100:.1f}%
        """)
        
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(
            x=city_revenue['City_Rank'][:20],
            y=city_revenue['Price (INR)'][:20],
            name='Revenue',
            marker_color='lightblue'
        ))
        fig_pareto.add_trace(go.Scatter(
            x=city_revenue['City_Rank'][:20],
            y=city_revenue['Cumulative_Percentage'][:20],
            name='Cumulative %',
            yaxis='y2',
            line=dict(color='red', width=3),
            mode='lines+markers'
        ))
        fig_pareto.add_hline(y=80, line_dash="dash", line_color="green", yref='y2')
        fig_pareto.update_layout(
            title='Pareto Chart: Top 20 Cities',
            xaxis_title='City Rank',
            yaxis_title='Revenue (₹)',
            yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0, 100]),
            height=400
        )
        st.plotly_chart(fig_pareto, width="stretch")
    
    with col2:
        st.subheader("📊 Correlation Analysis")
        
        correlation = df_filtered['Price (INR)'].corr(df_filtered['Rating'])
        
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
            x='Rating',
            y='Price (INR)',
            title='Price vs Rating (Sample)',
            trendline='ols',
            opacity=0.6
        )
        st.plotly_chart(fig_scatter, width="stretch")
    
    st.markdown('<h3 class="sub-header">📈 Key Statistics</h3>', unsafe_allow_html=True)
    
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    with stats_col1:
        st.metric("Unique States", df_filtered['State'].nunique())
    
    with stats_col2:
        st.metric("Unique Cities", df_filtered['City'].nunique())
    
    with stats_col3:
        st.metric("Unique Restaurants", df_filtered['Restaurant Name'].nunique())
    
    with stats_col4:
        st.metric("Unique Dishes", df_filtered['Dish Name'].nunique())

    # ── Menu Intelligence Matrix (BCG Framework) ─────────────────────────────
    st.markdown('<h3 class="sub-header">🍽️ Menu Intelligence Matrix</h3>', unsafe_allow_html=True)
    st.caption("BCG-style quadrant framework: classifies food categories by revenue share vs. weighted rating.")

    # ── Step 1: normalise category names (merge BURGERS/Burgers etc.) ─────────
    _exclude_pattern = (
        r'[()%&\d]|recommended|dotd|combo|deal|sale|fest|sharing|value|premium|'
        r'epic|exclusive|flash|limited|group|protein|session|special|collection|'
        r'tub|scooped|mcsaver|royal|jumbo|bucket|family|party|pack|offer|free|'
        r'discount|saving|upto|up to|newly|launched'
    )
    _df_mim = df_filtered.copy()
    _df_mim['_Cat_clean'] = _df_mim['Category'].str.strip().str.title()

    # Drop rows whose category name contains promo/deal language
    _df_mim = _df_mim[
        ~_df_mim['Category'].str.contains(r'[()%&\d]', regex=True, na=False) &
        ~_df_mim['Category'].str.lower().str.contains(_exclude_pattern, regex=True, na=False)
    ]

    # Merge near-duplicates via title-cased normalisation (BURGERS→Burgers, Cakes→Cake, etc.)
    _df_mim['_Cat_clean'] = (
        _df_mim['_Cat_clean']
        .str.replace(r'\bCakes\b', 'Cake', regex=True)
        .str.replace(r'\bBurgers\b', 'Burger', regex=True)
        .str.replace(r'\bRolls\b',   'Roll',   regex=True)
        .str.replace(r'\bPizzas\b',  'Pizza',  regex=True)
        .str.replace(r'\bBeverages\b', 'Beverage', regex=True)
        .str.replace(r'\bNoodles\b', 'Noodle', regex=True)
    )

    # ── Step 2: aggregate on clean names, min 200 orders ────────────────────
    cat_stats = (
        _df_mim.groupby('_Cat_clean')
        .agg(
            Revenue=('Price (INR)', 'sum'),
            Orders=('Price (INR)', 'count'),
            Weighted_Rating=('Rating', lambda x: np.average(
                x, weights=_df_mim.loc[x.index, 'Rating Count'].clip(lower=1)))
        )
        .reset_index()
        .rename(columns={'_Cat_clean': 'Category'})
    )
    cat_stats = cat_stats[cat_stats['Orders'] >= 100]

    # Top 15 by revenue → clean, readable BCG
    cat_stats = cat_stats.nlargest(15, 'Revenue').reset_index(drop=True)
    cat_stats['Revenue_Share'] = cat_stats['Revenue'] / cat_stats['Revenue'].sum() * 100
    rev_median    = cat_stats['Revenue_Share'].median()
    rating_median = cat_stats['Weighted_Rating'].median()

    def assign_quadrant(row):
        hi_rev    = row['Revenue_Share']    >= rev_median
        hi_rating = row['Weighted_Rating'] >= rating_median
        if hi_rev and hi_rating:
            return 'Stars'
        elif hi_rev and not hi_rating:
            return 'Cash Cows'
        elif not hi_rev and hi_rating:
            return 'Hidden Gems'
        else:
            return 'Review Needed'

    cat_stats['Quadrant'] = cat_stats.apply(assign_quadrant, axis=1)

    fig_mim = px.scatter(
        cat_stats,
        x='Revenue_Share', y='Weighted_Rating', size='Orders',
        color='Quadrant', text='Category',
        title='Menu Intelligence Matrix: Category Positioning',
        labels={'Revenue_Share': 'Revenue Share (%)', 'Weighted_Rating': 'Weighted Rating'},
        color_discrete_map={
            'Stars': '#FFD700', 'Hidden Gems': '#00BFFF',
            'Cash Cows': '#32CD32', 'Review Needed': '#FF4500'
        }
    )
    fig_mim.add_vline(x=rev_median,    line_dash='dash', line_color='gray', annotation_text='Revenue Median')
    fig_mim.add_hline(y=rating_median, line_dash='dash', line_color='gray', annotation_text='Rating Median')
    fig_mim.update_traces(textposition='top center')
    fig_mim.update_layout(height=550)
    st.plotly_chart(fig_mim, width='stretch')

    st.dataframe(
        cat_stats[['Category', 'Quadrant', 'Revenue_Share', 'Weighted_Rating', 'Orders']]
        .sort_values('Revenue_Share', ascending=False)
        .rename(columns={'Revenue_Share': 'Revenue Share (%)', 'Weighted_Rating': 'Weighted Rating'})
        .reset_index(drop=True),
        width='stretch'
    )

# ============================================================================
# TAB 6: SQL PIPELINE
# ============================================================================
with tab6:
    st.markdown('<h3 class="sub-header">🗄️ SQL Analytics Pipeline</h3>', unsafe_allow_html=True)
    st.info(
        "Raw order data is loaded from `swiggy_data.xlsx` into a SQLite database. "
        "All analytics below are produced by SQL queries running against that database — "
        "replicating a real data-engineering pipeline."
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
    st.dataframe(result_df, width='stretch')

    csv_bytes = result_df.to_csv(index=False).encode()
    st.download_button(
        label="📥 Download query result as CSV",
        data=csv_bytes,
        file_name=f"{query_name.replace(' ', '_').lower()}.csv",
        mime="text/csv",
    )

# ============================================================================
# TAB 7: EXPANSION STRATEGY
# ============================================================================
with tab7:
    st.markdown('<h3 class="sub-header">🏙️ City Expansion Opportunity Index</h3>', unsafe_allow_html=True)
    st.caption("""
    A 4-signal composite model (0–100) scoring cities by: **Revenue Growth (30%)** + **Weighted Rating (25%)** + **Order Density (25%)** + **Category Diversity (20%)**.
    """)

    df_filtered['_Order_Date_dt'] = pd.to_datetime(df_filtered['Order Date'])
    mid_date = df_filtered['_Order_Date_dt'].min() + (df_filtered['_Order_Date_dt'].max() - df_filtered['_Order_Date_dt'].min()) / 2
    city_h1 = df_filtered[df_filtered['_Order_Date_dt'] <  mid_date].groupby('City')['Price (INR)'].sum()
    city_h2 = df_filtered[df_filtered['_Order_Date_dt'] >= mid_date].groupby('City')['Price (INR)'].sum()

    city_agg = (
        df_filtered.groupby('City')
        .agg(
            Orders=('Price (INR)', 'count'),
            Revenue=('Price (INR)', 'sum'),
            Weighted_Rating=('Rating', lambda x: np.average(
                x, weights=df_filtered.loc[x.index, 'Rating Count'].clip(lower=1))),
            Restaurants=('Restaurant Name', 'nunique'),
            Categories=('Category', 'nunique')
        )
        .reset_index()
    )
    city_agg['Growth_Rate']   = (city_agg['City'].map(city_h2).fillna(0) /
                                  city_agg['City'].map(city_h1).replace(0, np.nan).fillna(1)) - 1
    city_agg['Order_Density'] = city_agg['Orders'] / city_agg['Restaurants'].replace(0, np.nan)
    city_agg['Cat_Diversity'] = city_agg['Categories']

    exp_scaler = MinMaxScaler()
    features = ['Growth_Rate', 'Weighted_Rating', 'Order_Density', 'Cat_Diversity']
    city_agg[features] = city_agg[features].fillna(0)
    norm = exp_scaler.fit_transform(city_agg[features])
    city_agg['Opportunity_Score'] = (
        norm[:, 0] * 0.30 + norm[:, 1] * 0.25 +
        norm[:, 2] * 0.25 + norm[:, 3] * 0.20
    ) * 100
    city_agg = city_agg.sort_values('Opportunity_Score', ascending=False).reset_index(drop=True)

    rev_med = city_agg['Revenue'].median()
    opp_med = city_agg['Opportunity_Score'].median()

    def city_quadrant(row):
        hi_rev = row['Revenue']           >= rev_med
        hi_opp = row['Opportunity_Score'] >= opp_med
        if hi_rev and hi_opp:
            return 'Stars'
        elif not hi_rev and hi_opp:
            return 'Untapped'
        elif hi_rev and not hi_opp:
            return 'Emerging'
        else:
            return 'Low Priority'

    city_agg['City_Tier'] = city_agg.apply(city_quadrant, axis=1)

    fig_a1 = px.scatter(
        city_agg,
        x='Revenue', y='Opportunity_Score',
        size='Orders', color='City_Tier',
        hover_name='City',
        title='City Expansion Opportunity Index',
        labels={'Revenue': 'Total Revenue (INR)', 'Opportunity_Score': 'Opportunity Score (0-100)'},
        color_discrete_map={
            'Stars': '#FFD700', 'Untapped': '#00BFFF',
            'Emerging': '#32CD32', 'Low Priority': '#D3D3D3'
        }
    )
    fig_a1.add_vline(x=rev_med, line_dash='dash', line_color='gray')
    fig_a1.add_hline(y=opp_med, line_dash='dash', line_color='gray')
    fig_a1.update_layout(height=550)
    st.plotly_chart(fig_a1, width='stretch')

    col1, col2 = st.columns(2)
    with col1:
        fig_top10 = px.bar(
            city_agg.head(10),
            x='Opportunity_Score', y='City',
            orientation='h', color='Opportunity_Score',
            color_continuous_scale='Blues',
            title='Top 10 Cities by Opportunity Score'
        )
        fig_top10.update_layout(height=400, yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig_top10, width='stretch')
    with col2:
        st.markdown("**Top 10 Expansion Targets**")
        st.dataframe(
            city_agg[['City', 'Opportunity_Score', 'City_Tier', 'Orders', 'Revenue']].head(10)
            .rename(columns={'Opportunity_Score': 'Score', 'City_Tier': 'Tier'})
            .reset_index(drop=True),
            width='stretch'
        )

    st.markdown('<h3 class="sub-header">🏥 Restaurant Health Score</h3>', unsafe_allow_html=True)
    st.caption("""
    Composite viability score (0–100) per restaurant: **Revenue 40%** + **Rating 30%** + **Orders 20%** + **Recency 10%**.
    """)

    df_filtered['_Order_Date_dt2'] = pd.to_datetime(df_filtered['Order Date'])
    snapshot_date = df_filtered['_Order_Date_dt2'].max() + pd.Timedelta(days=1)

    rest_agg = (
        df_filtered.groupby('Restaurant Name')
        .agg(
            Revenue=('Price (INR)', 'sum'),
            Orders=('Price (INR)', 'count'),
            Weighted_Rating=('Rating', lambda x: np.average(
                x, weights=df_filtered.loc[x.index, 'Rating Count'].clip(lower=1))),
            Last_Order=('_Order_Date_dt2', 'max')
        )
        .reset_index()
    )
    rest_agg['Revenue_Share'] = rest_agg['Revenue'] / rest_agg['Revenue'].sum() * 100
    rest_agg['Recency_Days']  = (snapshot_date - rest_agg['Last_Order']).dt.days

    hs_scaler = MinMaxScaler()
    rest_agg[['Rev_N', 'Rating_N', 'Orders_N']] = hs_scaler.fit_transform(
        rest_agg[['Revenue_Share', 'Weighted_Rating', 'Orders']]
    )
    rest_agg['Recency_N'] = 1 - hs_scaler.fit_transform(rest_agg[['Recency_Days']])
    rest_agg['Health_Score'] = (
        rest_agg['Rev_N']     * 0.40 +
        rest_agg['Rating_N']  * 0.30 +
        rest_agg['Orders_N']  * 0.20 +
        rest_agg['Recency_N'] * 0.10
    ) * 100

    def health_tier(score):
        if score >= 75:
            return 'Champion'
        elif score >= 50:
            return 'Healthy'
        elif score >= 25:
            return 'At Risk'
        else:
            return 'Critical'

    rest_agg['Health_Tier'] = rest_agg['Health_Score'].apply(health_tier)

    col1, col2 = st.columns(2)
    with col1:
        fig_top_r = px.bar(
            rest_agg.nlargest(15, 'Health_Score'),
            x='Health_Score', y='Restaurant Name',
            orientation='h', color='Health_Score',
            color_continuous_scale='Greens',
            title='Top 15 Champion Restaurants'
        )
        fig_top_r.update_layout(height=500, yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig_top_r, width='stretch')
    with col2:
        fig_bot_r = px.bar(
            rest_agg.nsmallest(15, 'Health_Score'),
            x='Health_Score', y='Restaurant Name',
            orientation='h', color='Health_Score',
            color_continuous_scale='Reds_r',
            title='Bottom 15 At-Risk Restaurants'
        )
        fig_bot_r.update_layout(height=500, yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig_bot_r, width='stretch')

    tier_counts = rest_agg['Health_Tier'].value_counts().reset_index()
    tier_counts.columns = ['Tier', 'Count']
    fig_tier = px.bar(
        tier_counts, x='Tier', y='Count', color='Tier',
        color_discrete_map={'Champion': '#FFD700', 'Healthy': '#32CD32', 'At Risk': '#FFA500', 'Critical': '#FF4500'},
        title='Restaurant Health Tier Distribution'
    )
    st.plotly_chart(fig_tier, width='stretch')

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🍽️ <strong>Swiggy Market Intelligence Engine</strong> | Decision-Support Analytics Platform</p>
    <p>Built with Python • Pandas • Plotly • SQLite • Streamlit</p>
</div>
""", unsafe_allow_html=True)
