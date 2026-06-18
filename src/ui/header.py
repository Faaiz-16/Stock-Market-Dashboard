"""
Dashboard header component.
"""

import streamlit as st


def render_header(symbol: str | None = None) -> None:
    """
    Display the main dashboard header with optional active stock symbol.

    Args:
        symbol: Currently selected stock ticker
    """
    subtitle = (
        f"Tracking live data for **{symbol}**"
        if symbol
        else "Track and visualize live stock market data"
    )

    st.markdown(
        f"""
        <div class="dashboard-header">
            <h1>📈 Real-Time Stock Market Dashboard</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
