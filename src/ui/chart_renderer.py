"""
Chart rendering component for the Streamlit dashboard.

Displays all five interactive Plotly charts in a tabbed layout.
"""

import streamlit as st

from src.data_processor import ProcessedStockData
from src.ui.charts import (
    create_candlestick_chart,
    create_combined_price_volume_chart,
    create_daily_returns_chart,
    create_line_chart,
    create_moving_average_chart,
    create_volume_chart,
)


def render_charts(processed: ProcessedStockData) -> None:
    """
    Render all interactive Plotly charts for the selected stock.

    Charts are displayed in tabs so the dashboard stays clean and
    each chart can be explored independently with zoom/pan/hover.

    Args:
        processed: Processed stock data from the data pipeline
    """
    symbol = processed["symbol"]
    history = processed["history"]

    st.markdown('<p class="section-header">Price Charts</p>', unsafe_allow_html=True)

    # Tab layout — one tab per chart type
    (
        tab_line,
        tab_candle,
        tab_volume,
        tab_returns,
        tab_ma,
        tab_overview,
    ) = st.tabs(
        [
            "📈 Line Chart",
            "🕯️ Candlestick",
            "📊 Volume",
            "📉 Daily Returns",
            "📐 Moving Avg",
            "🔍 Overview",
        ]
    )

    with tab_line:
        st.plotly_chart(
            create_line_chart(history, symbol),
            use_container_width=True,
            key="chart_line",
        )

    with tab_candle:
        st.plotly_chart(
            create_candlestick_chart(history, symbol),
            use_container_width=True,
            key="chart_candlestick",
        )

    with tab_volume:
        st.plotly_chart(
            create_volume_chart(history, symbol),
            use_container_width=True,
            key="chart_volume",
        )

    with tab_returns:
        st.plotly_chart(
            create_daily_returns_chart(history, symbol),
            use_container_width=True,
            key="chart_returns",
        )

    with tab_ma:
        st.plotly_chart(
            create_moving_average_chart(history, symbol),
            use_container_width=True,
            key="chart_ma",
        )

    with tab_overview:
        st.plotly_chart(
            create_combined_price_volume_chart(history, symbol),
            use_container_width=True,
            key="chart_overview",
        )
