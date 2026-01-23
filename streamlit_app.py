import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page Configuration
st.set_page_config(
    page_title="🍽️ Swiggy Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .header {
        color: #FF6B35;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subheader {
        color: #004E89;
        font-size: 1.5em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Load and cache data
@st.cache_data
def load_data():
    df = pd.read_excel('swiggy_data.xlsx')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    
    # Feature engineering
    non_veg_keywords = ['chicken', 'mutton', 'fish', 'egg', 'prawn', 'meat', 'biryani', 'kebab', 'seafood', "non-veg", "non veg", "kabab"]
    df["Food Category"] = np.where(df['Dish Name'].str.lower().str.contains('|'.join(non_veg_keywords), na=False), 'Non-Veg', 'Veg')
    
    df["Year-Month"] = df["Order Date"].dt.to_period("M").astype(str)
    df["DayName"] = df["Order Date"].dt.day_name()
    df["order_Date"] = pd.to_datetime(df["Order Date"])
    df["Quarter"] = df["order_Date"].dt.to_period("Q").astype(str)
    
    return df

# Load data
df = load_data()

# Sidebar Filters
st.sidebar.markdown("## 🎯 Filters")
st.sidebar.markdown("---")

# Date Range Filter
date_range = st.sidebar.date_input(
    "Select Date Range:",
    value=(df['Order Date'].min().date(), df['Order Date'].max().date()),
    min_value=df['Order Date'].min().date(),
    max_value=df['Order Date'].max().date()
)

# Food Category Filter
selected_category = st.sidebar.multiselect(
    "Food Category:",
    options=df['Food Category'].unique(),
    default=df['Food Category'].unique()
)

# State Filter
selected_state = st.sidebar.multiselect(
    "State:",
    options=sorted(df['State'].unique()),
    default=sorted(df['State'].unique())
)

# Filter data based on selections
filtered_df = df[
    (df['Order Date'].dt.date >= date_range[0]) &
    (df['Order Date'].dt.date <= date_range[1]) &
    (df['Food Category'].isin(selected_category)) &
    (df['State'].isin(selected_state))
]

# Main Header
st.markdown('<div class="header">🍽️ Swiggy Sales Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")

# KPI Metrics Section
st.markdown('<div class="subheader">📊 Key Performance Indicators</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_sales = filtered_df['Price (INR)'].sum()
    st.metric(
        label="💰 Total Sales",
        value=f"₹{total_sales:,.0f}",
        delta=f"₹{total_sales/len(filtered_df):,.0f} per order" if len(filtered_df) > 0 else "No data"
    )

with col2:
    total_orders = len(filtered_df)
    st.metric(
        label="📦 Total Orders",
        value=f"{total_orders:,}",
        delta=f"{total_orders/len(df['City'].unique()):,.0f} per city" if len(df['City'].unique()) > 0 else "No data"
    )

with col3:
    avg_order_value = filtered_df['Price (INR)'].mean() if len(filtered_df) > 0 else 0
    st.metric(
        label="💵 Avg Order Value",
        value=f"₹{avg_order_value:,.0f}",
        delta="Mean order value"
    )

with col4:
    avg_rating = filtered_df['Rating'].mean() if len(filtered_df) > 0 else 0
    st.metric(
        label="⭐ Avg Rating",
        value=f"{avg_rating:.2f}/5.0",
        delta=f"{len(filtered_df[filtered_df['Rating'] >= 4])} high-rated orders"
    )

with col5:
    unique_cities = filtered_df['City'].nunique()
    st.metric(
        label="🏙️ Cities Covered",
        value=f"{unique_cities}",
        delta=f"{unique_cities} active cities"
    )

st.markdown("---")

# Tab Navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Sales Trends", "🍴 Category Analysis", "🗺️ Geographic Insights", "📊 Quarterly Performance", "👥 Customer Segments"]
)

# TAB 1: Sales Trends
with tab1:
    st.markdown("### Sales Trends Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Monthly Revenue Trend")
        monthly_data = filtered_df.groupby('Year-Month')['Price (INR)'].sum().reset_index()
        
        fig_monthly = px.line(
            monthly_data,
            x='Year-Month',
            y='Price (INR)',
            markers=True,
            title='Monthly Revenue Trend',
            labels={'Price (INR)': 'Revenue (₹)', 'Year-Month': 'Month'},
            line_shape='spline'
        )
        fig_monthly.update_layout(height=400, hovermode='x unified')
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col2:
        st.markdown("#### Daily Sales Pattern")
        daily_data = filtered_df.groupby('DayName')['Price (INR)'].sum().reindex(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ).reset_index()
        
        fig_daily = px.bar(
            daily_data,
            x='DayName',
            y='Price (INR)',
            title='Sales by Day of Week',
            labels={'Price (INR)': 'Revenue (₹)', 'DayName': 'Day'},
            color='Price (INR)',
            color_continuous_scale='Blues'
        )
        fig_daily.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_daily, use_container_width=True)

# TAB 2: Category Analysis
with tab2:
    st.markdown("### Food Category Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Revenue Distribution (Veg vs Non-Veg)")
        food_revenue = filtered_df.groupby('Food Category')['Price (INR)'].sum().reset_index()
        
        fig_pie = px.pie(
            food_revenue,
            names='Food Category',
            values='Price (INR)',
            title='Revenue by Food Category',
            hole=0.4,
            color_discrete_map={'Veg': '#2ecc71', 'Non-Veg': '#e74c3c'}
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("#### Orders Count by Category")
        category_orders = filtered_df.groupby('Food Category').size().reset_index(name='Orders')
        
        fig_cat_bar = px.bar(
            category_orders,
            x='Food Category',
            y='Orders',
            title='Order Count by Food Category',
            labels={'Orders': 'Number of Orders'},
            color='Food Category',
            color_discrete_map={'Veg': '#2ecc71', 'Non-Veg': '#e74c3c'}
        )
        fig_cat_bar.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_cat_bar, use_container_width=True)

# TAB 3: Geographic Insights
with tab3:
    st.markdown("### Geographic Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Sales by State")
        state_data = filtered_df.groupby('State')['Price (INR)'].sum().reset_index().sort_values('Price (INR)', ascending=False).head(15)
        
        fig_state = px.barh(
            state_data,
            x='Price (INR)',
            y='State',
            title='Top 15 States by Revenue',
            labels={'Price (INR)': 'Revenue (₹)'},
            color='Price (INR)',
            color_continuous_scale='Viridis'
        )
        fig_state.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_state, use_container_width=True)
    
    with col2:
        st.markdown("#### Top 10 Cities by Sales")
        top_cities = filtered_df.groupby('City')['Price (INR)'].sum().nlargest(10).reset_index()
        
        fig_cities = px.bar(
            top_cities,
            x='City',
            y='Price (INR)',
            title='Top 10 Cities by Revenue',
            labels={'Price (INR)': 'Revenue (₹)'},
            color='Price (INR)',
            color_continuous_scale='Reds'
        )
        fig_cities.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig_cities, use_container_width=True)

# TAB 4: Quarterly Performance
with tab4:
    st.markdown("### Quarterly Performance Analysis")
    
    quarterly_data = filtered_df.groupby('Quarter').agg({
        'Price (INR)': 'sum',
        'Rating': 'mean',
        'Order Date': 'count'
    }).reset_index()
    quarterly_data.columns = ['Quarter', 'Total Sales', 'Avg Rating', 'Orders']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_q_sales = px.bar(
            quarterly_data,
            x='Quarter',
            y='Total Sales',
            title='Quarterly Revenue',
            labels={'Total Sales': 'Revenue (₹)', 'Quarter': 'Quarter'},
            color='Total Sales',
            color_continuous_scale='Blues'
        )
        fig_q_sales.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_q_sales, use_container_width=True)
    
    with col2:
        fig_q_orders = px.bar(
            quarterly_data,
            x='Quarter',
            y='Orders',
            title='Quarterly Orders',
            labels={'Orders': 'Number of Orders'},
            color='Orders',
            color_continuous_scale='Greens'
        )
        fig_q_orders.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_q_orders, use_container_width=True)
    
    with col3:
        fig_q_rating = px.bar(
            quarterly_data,
            x='Quarter',
            y='Avg Rating',
            title='Quarterly Avg Rating',
            labels={'Avg Rating': 'Rating'},
            color='Avg Rating',
            color_continuous_scale='Reds'
        )
        fig_q_rating.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_q_rating, use_container_width=True)

# TAB 5: Customer Segments
with tab5:
    st.markdown("### Customer Segmentation Analysis")
    
    # Create segments
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['Value_Segment'] = pd.cut(
        filtered_df_copy['Price (INR)'],
        bins=[0, 200, 500, 1000, float('inf')],
        labels=['Budget', 'Standard', 'Premium', 'Luxury']
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Revenue by Customer Segment")
        segment_revenue = filtered_df_copy.groupby('Value_Segment')['Price (INR)'].sum().reset_index()
        
        fig_seg_revenue = px.pie(
            segment_revenue,
            names='Value_Segment',
            values='Price (INR)',
            title='Revenue Distribution by Segment',
            hole=0.3,
            color_discrete_sequence=['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
        )
        fig_seg_revenue.update_layout(height=400)
        st.plotly_chart(fig_seg_revenue, use_container_width=True)
    
    with col2:
        st.markdown("#### Orders by Customer Segment")
        segment_orders = filtered_df_copy.groupby('Value_Segment').size().reset_index(name='Orders')
        
        fig_seg_orders = px.bar(
            segment_orders,
            x='Value_Segment',
            y='Orders',
            title='Order Count by Segment',
            labels={'Orders': 'Number of Orders'},
            color='Value_Segment',
            color_discrete_sequence=['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
        )
        fig_seg_orders.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_seg_orders, use_container_width=True)
    
    # Segment Statistics Table
    st.markdown("#### Segment Statistics")
    segment_stats = filtered_df_copy.groupby('Value_Segment').agg({
        'Price (INR)': ['sum', 'mean', 'count'],
        'Rating': 'mean'
    }).round(2)
    segment_stats.columns = ['Total Revenue', 'Avg Order Value', 'Order Count', 'Avg Rating']
    segment_stats['Revenue %'] = (segment_stats['Total Revenue'] / segment_stats['Total Revenue'].sum() * 100).round(2)
    
    st.dataframe(segment_stats, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>📊 <strong>Swiggy Sales Analytics Dashboard</strong></p>
    <p>Built with Streamlit | Python | Plotly | Pandas</p>
    <p>🔗 <a href='https://github.com/Mounusha25/swiggy_analysis'>View on GitHub</a></p>
</div>
""", unsafe_allow_html=True)
