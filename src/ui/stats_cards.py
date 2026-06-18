"""
Statistics cards component for displaying financial indicators.
"""

import streamlit as st

from src.data_processor import StockIndicators
from src.ui.formatters import format_change_percent, format_price, format_volume, get_change_delta


def render_statistics_cards(indicators: StockIndicators) -> None:
    """
    Display all financial indicator cards in a professional grid layout.

    Shows 9 metrics across 3 rows:
        Row 1: Current Price, Open, High, Low
        Row 2: Previous Close, Volume, Daily Change, 7-Day MA
        Row 3: 30-Day MA

    Args:
        indicators: Calculated financial indicators from data_processor
    """
    st.markdown('<p class="section-header">Key Statistics</p>', unsafe_allow_html=True)

    # Row 1 — primary price metrics
    row1 = st.columns(4)
    row1[0].metric(
        label="Current Price",
        value=format_price(indicators["current_price"]),
        delta=get_change_delta(indicators["daily_change_pct"]),
        delta_color="normal",
    )
    row1[1].metric(label="Open", value=format_price(indicators["open_price"]))
    row1[2].metric(label="High", value=format_price(indicators["high"]))
    row1[3].metric(label="Low", value=format_price(indicators["low"]))

    # Row 2 — volume and moving averages
    row2 = st.columns(4)
    row2[0].metric(
        label="Previous Close",
        value=format_price(indicators["previous_close"]),
    )
    row2[1].metric(label="Volume", value=format_volume(indicators["volume"]))
    row2[2].metric(
        label="Daily Change",
        value=format_change_percent(indicators["daily_change_pct"]),
    )
    row2[3].metric(label="7-Day MA", value=format_price(indicators["ma_7"]))

    # Row 3 — long-term moving average
    row3 = st.columns(4)
    row3[0].metric(label="30-Day MA", value=format_price(indicators["ma_30"]))


def render_stock_summary(symbol: str, data_source: str, date_range: str) -> None:
    """
    Display a summary bar with the active stock and data context.

    Args:
        symbol: Active stock ticker
        data_source: API source name
        date_range: Selected historical window
    """
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        st.markdown(f"### {symbol}")
    with col2:
        st.markdown(f"**Period:** `{date_range}`")
    with col3:
        st.markdown(f"**Source:** `{data_source}`")
