"""
Analytics section UI for the Stock Market Dashboard.

Displays period-level statistics in a professional card layout.
"""

import streamlit as st

from src.analytics import AnalyticsSummary, calculate_analytics
from src.data_processor import ProcessedStockData
from src.ui.formatters import format_price, format_volume


def render_analytics_section(processed: ProcessedStockData) -> None:
    """
    Render the analytics section with period statistics.

    Displays:
        - Highest price (with date)
        - Lowest price (with date)
        - Average closing price
        - Volatility (daily return std dev)
        - Total trading volume
        - Trading days count

    Args:
        processed: Processed stock data from the data pipeline
    """
    analytics = calculate_analytics(processed["history"])
    symbol = processed["symbol"]
    date_range = processed["date_range"]

    st.markdown('<p class="section-header">Analytics</p>', unsafe_allow_html=True)
    st.caption(f"Period analysis for **{symbol}** over **{date_range}**")

    # Row 1 — price extremes and average
    row1 = st.columns(3)
    row1[0].metric(
        label="Highest Price",
        value=format_price(analytics["highest_price"]),
        delta=f"on {analytics['highest_price_date']}",
        delta_color="off",
    )
    row1[1].metric(
        label="Lowest Price",
        value=format_price(analytics["lowest_price"]),
        delta=f"on {analytics['lowest_price_date']}",
        delta_color="off",
    )
    row1[2].metric(
        label="Average Close",
        value=format_price(analytics["average_close"]),
    )

    # Row 2 — volatility and volume
    row2 = st.columns(3)
    row2[0].metric(
        label="Volatility",
        value=f"{analytics['volatility']:.2f}%",
        help="Standard deviation of daily returns over the selected period.",
    )
    row2[1].metric(
        label="Total Volume",
        value=format_volume(analytics["total_volume"]),
    )
    row2[2].metric(
        label="Trading Days",
        value=str(analytics["trading_days"]),
    )

    # Summary insight box
    price_range = analytics["highest_price"] - analytics["lowest_price"]
    st.info(
        f"**{symbol}** moved between "
        f"**{format_price(analytics['lowest_price'])}** and "
        f"**{format_price(analytics['highest_price'])}** "
        f"(range: **{format_price(price_range)}**) across "
        f"**{analytics['trading_days']}** trading days."
    )


def get_analytics_summary(processed: ProcessedStockData) -> AnalyticsSummary:
    """
    Calculate and return analytics without rendering UI.

    Useful for testing and downstream modules.

    Args:
        processed: Processed stock data

    Returns:
        AnalyticsSummary dictionary
    """
    return calculate_analytics(processed["history"])
