"""
Real-Time Stock Market Dashboard
=================================
Main Streamlit application entry point.

Fully integrated Stock Market Dashboard (Modules 1–8 complete):
    Module 1 — Project setup
    Module 2 — Stock data fetching   (src/data_fetcher.py)
    Module 3 — Data processing       (src/data_processor.py)
    Module 4 — Dashboard UI          (src/ui/)
    Module 5 — Plotly visualizations (src/ui/charts.py)
    Module 6 — Analytics section     (src/analytics.py)
    Module 7 — Final integration     (src/pipeline.py)
    Module 8 — Deployment & docs     (README.md, runtime.txt)

Run locally:
    streamlit run app.py

Deploy:
    See README.md → Deployment (Streamlit Community Cloud)
"""

import streamlit as st

from src.ui.layout import render_dashboard


def configure_page() -> None:
    """Set Streamlit page configuration (title, layout, icon)."""
    st.set_page_config(
        page_title="Stock Market Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def main() -> None:
    """Run the fully integrated Stock Market Dashboard."""
    configure_page()
    render_dashboard()


if __name__ == "__main__":
    main()
