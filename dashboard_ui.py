"""Shared Streamlit layout helpers for the Swiggy dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from generate_excel_report import generate_report


def configure_page() -> None:
    st.set_page_config(
        page_title="Swiggy Market Intelligence Engine",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_styles() -> None:
    st.markdown(
        """
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
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        '<h1 class="main-header">🍽️ Swiggy Market Intelligence Engine</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "**Decision-support analytics for Swiggy's growth, expansion, and restaurant strategy**",
        unsafe_allow_html=True,
    )


def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("## 🔍 Filters")

    date_range = st.sidebar.date_input(
        "Select Date Range:",
        value=(df["Order Date"].min().date(), df["Order Date"].max().date()),
        min_value=df["Order Date"].min().date(),
        max_value=df["Order Date"].max().date(),
    )

    all_states = sorted(df["State"].unique())
    selected_states = st.sidebar.multiselect("Select States:", all_states, default=all_states[:5])

    selected_food = st.sidebar.selectbox("Food Category:", ["Both", "Veg", "Non-Veg"], index=0)

    df_filtered = df[
        (df["Order Date"].dt.date >= date_range[0])
        & (df["Order Date"].dt.date <= date_range[1])
        & (df["State"].isin(selected_states))
    ].copy()

    if selected_food != "Both":
        df_filtered = df_filtered[df_filtered["Food Category"] == selected_food].copy()

    st.sidebar.markdown("---")
    with st.sidebar.expander("ℹ️ About this project"):
        st.markdown(
            """
            **Swiggy Market Intelligence Engine** turns 197K+ food delivery orders into actionable strategy.

            **3 Proprietary Frameworks:**
            - 🍽️ Menu Intelligence Matrix (BCG-style)
            - 🏙️ City Expansion Opportunity Index
            - 🏥 Restaurant Health Score

            Built with Python • Pandas • Plotly • SQLite • Streamlit
            """
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Export Report")
    if st.sidebar.button("Generate Excel KPI Report"):
        with st.spinner("Building 20-sheet Excel report…"):
            st.session_state["excel_bytes"] = generate_report(df_filtered)

    if st.session_state.get("excel_bytes"):
        st.sidebar.download_button(
            label="📥 Download Excel Report",
            data=st.session_state["excel_bytes"],
            file_name="swiggy_kpi_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    return df_filtered


def render_kpis(df_filtered: pd.DataFrame) -> None:
    st.markdown('<h2 class="sub-header">📊 Key Performance Indicators</h2>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"₹{df_filtered['Price (INR)'].sum():,.0f}")
    with col2:
        st.metric("Total Orders", f"{len(df_filtered):,}")
    with col3:
        st.metric("Avg Order Value", f"₹{df_filtered['Price (INR)'].mean():,.0f}")
    with col4:
        st.metric("Avg Rating", f"{df_filtered['Rating'].mean():.2f} / 5.0")


def render_footer() -> None:
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>🍽️ <strong>Swiggy Market Intelligence Engine</strong> | Decision-Support Analytics Platform</p>
            <p>Built with Python • Pandas • Plotly • SQLite • Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
