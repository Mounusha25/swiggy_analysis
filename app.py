"""Streamlit entrypoint for the Swiggy Market Intelligence dashboard."""

from __future__ import annotations

import warnings

import pandas as pd
import streamlit as st

from analytics_models import prepare_order_data
from dashboard_tabs import render_tabs
from dashboard_ui import (
    configure_page,
    inject_styles,
    render_footer,
    render_header,
    render_kpis,
    render_sidebar,
)

warnings.filterwarnings("ignore")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel("swiggy_data.xlsx")
    return prepare_order_data(df, include_synthetic_hour=True)


def main() -> None:
    configure_page()
    inject_styles()

    try:
        df = load_data()
    except FileNotFoundError:
        st.error("❌ Error: 'swiggy_data.xlsx' not found in the current directory.")
        st.stop()

    render_header()
    df_filtered = render_sidebar(df)
    render_kpis(df_filtered)
    render_tabs(df, df_filtered)
    render_footer()


if __name__ == "__main__":
    main()
