import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================
st.set_page_config(
    page_title="Swiggy Sales Analytics",
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
st.markdown('<h1 class="main-header">🍽️ Swiggy Sales Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**End-to-end data analysis of Swiggy food delivery platform**", unsafe_allow_html=True)

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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Overview", "🗺️ Geographic", "🎯 Segments", "📉 Trends", "💡 Insights"])

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
        st.plotly_chart(fig_food, use_container_width=True)
    
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
        st.plotly_chart(fig_quarterly, use_container_width=True)
    
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
    st.plotly_chart(fig_daily, use_container_width=True)

# ============================================================================
# TAB 2: GEOGRAPHIC
# ============================================================================
with tab2:
    st.markdown('<h3 class="sub-header">Geographic Performance</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        # Top states by revenue
        state_revenue = df_filtered.groupby("State", as_index=False)['Price (INR)'].sum().sort_values('Price (INR)', ascending=True).tail(15)
        
        fig_state = px.barh(
            state_revenue,
            x="Price (INR)",
            y="State",
            title="Top 15 States by Revenue",
            color="Price (INR)",
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_state, use_container_width=True)
    
    with col2:
        # Top cities
        city_revenue = (df_filtered.groupby("City")[("Price (INR)")]
                       .sum()
                       .nlargest(10)
                       .sort_values()
                       .reset_index())
        
        fig_city = px.barh(
            city_revenue,
            x="Price (INR)",
            y="City",
            title="Top 10 Cities by Revenue",
            color="Price (INR)",
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_city, use_container_width=True)
    
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
    st.plotly_chart(fig_state_scatter, use_container_width=True)

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
        st.plotly_chart(fig_segment_pie, use_container_width=True)
    
    with col2:
        fig_segment_orders = px.bar(
            segment_analysis,
            x='Value_Segment',
            y='Orders',
            title='Order Count by Segment',
            color='Orders',
            color_continuous_scale='Plasma'
        )
        st.plotly_chart(fig_segment_orders, use_container_width=True)
    
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
    st.plotly_chart(fig_heatmap, use_container_width=True)

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
        st.plotly_chart(fig_monthly, use_container_width=True)
    
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
    st.plotly_chart(fig_growth, use_container_width=True)

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
        st.plotly_chart(fig_pareto, use_container_width=True)
    
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
        
        fig_scatter = px.scatter(
            df_filtered.sample(min(1000, len(df_filtered))),
            x='Rating',
            y='Price (INR)',
            title='Price vs Rating (Sample)',
            trendline='ols',
            opacity=0.6
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
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

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🍽️ <strong>Swiggy Sales Analytics</strong> | Data Analysis & Interactive Dashboard</p>
    <p>Built with Python • Pandas • Plotly • Streamlit</p>
</div>
""", unsafe_allow_html=True)
