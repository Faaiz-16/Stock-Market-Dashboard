"""
Plotly chart components for the Stock Market Dashboard.

Creates five interactive charts from processed stock history data:
    - Line chart (closing price)
    - Candlestick chart (OHLC)
    - Volume chart
    - Daily returns chart
    - Moving average chart
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.settings import MA_LONG_PERIOD, MA_SHORT_PERIOD

# ---------------------------------------------------------------------------
# Chart styling constants
# ---------------------------------------------------------------------------
CHART_HEIGHT: int = 420
COLOR_PRICE: str = "#1f77b4"
COLOR_MA_SHORT: str = "#ff7f0e"
COLOR_MA_LONG: str = "#9467bd"
COLOR_UP: str = "#2ecc71"
COLOR_DOWN: str = "#e74c3c"
COLOR_VOLUME: str = "#5b9bd5"

# Shared layout settings for a consistent look across all charts
CHART_LAYOUT: dict = {
    "template": "plotly_white",
    "hovermode": "x unified",
    "margin": dict(l=40, r=40, t=60, b=40),
    "legend": dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
}


def _prepare_chart_data(frame: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for Plotly charts.

    Ensures Date is a plain datetime column (no timezone issues in charts).
    """
    chart_data = frame.copy()
    chart_data["Date"] = pd.to_datetime(chart_data["Date"]).dt.tz_localize(None)
    return chart_data


def create_line_chart(frame: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create an interactive line chart of closing prices.

    Args:
        frame: Processed history with Date and Close columns
        symbol: Stock ticker for the chart title

    Returns:
        Plotly Figure object
    """
    data = _prepare_chart_data(frame)

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Close"],
            mode="lines",
            name="Close Price",
            line=dict(color=COLOR_PRICE, width=2),
            hovertemplate="Date: %{x}<br>Close: $%{y:.2f}<extra></extra>",
        )
    )

    figure.update_layout(
        **CHART_LAYOUT,
        height=CHART_HEIGHT,
        title=dict(text=f"{symbol} — Closing Price", x=0.01),
        xaxis_title="Date",
        yaxis_title="Price (USD)",
    )

    return figure


def create_candlestick_chart(frame: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create an interactive candlestick (OHLC) chart.

    Green candles = price closed higher than it opened.
    Red candles   = price closed lower than it opened.

    Args:
        frame: Processed history with OHLC columns
        symbol: Stock ticker for the chart title

    Returns:
        Plotly Figure object
    """
    data = _prepare_chart_data(frame)

    figure = go.Figure(
        data=[
            go.Candlestick(
                x=data["Date"],
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name="OHLC",
                increasing_line_color=COLOR_UP,
                decreasing_line_color=COLOR_DOWN,
                increasing_fillcolor=COLOR_UP,
                decreasing_fillcolor=COLOR_DOWN,
            )
        ]
    )

    figure.update_layout(
        **CHART_LAYOUT,
        height=CHART_HEIGHT,
        title=dict(text=f"{symbol} — Candlestick Chart", x=0.01),
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
    )

    return figure


def create_volume_chart(frame: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create an interactive volume bar chart.

    Bars are coloured green on up-days (close >= open) and red on down-days.

    Args:
        frame: Processed history with Date, Open, Close, Volume columns
        symbol: Stock ticker for the chart title

    Returns:
        Plotly Figure object
    """
    data = _prepare_chart_data(frame)

    # Colour each bar based on whether the day was bullish or bearish
    bar_colors = [
        COLOR_UP if close >= open else COLOR_DOWN
        for close, open in zip(data["Close"], data["Open"])
    ]

    figure = go.Figure()
    figure.add_trace(
        go.Bar(
            x=data["Date"],
            y=data["Volume"],
            name="Volume",
            marker_color=bar_colors,
            hovertemplate="Date: %{x}<br>Volume: %{y:,}<extra></extra>",
        )
    )

    figure.update_layout(
        **CHART_LAYOUT,
        height=CHART_HEIGHT,
        title=dict(text=f"{symbol} — Trading Volume", x=0.01),
        xaxis_title="Date",
        yaxis_title="Volume",
    )

    return figure


def create_daily_returns_chart(frame: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create an interactive daily returns (%) bar chart.

    Args:
        frame: Processed history with Date and Daily_Return columns
        symbol: Stock ticker for the chart title

    Returns:
        Plotly Figure object
    """
    data = _prepare_chart_data(frame)

    bar_colors = [
        COLOR_UP if value >= 0 else COLOR_DOWN for value in data["Daily_Return"]
    ]

    figure = go.Figure()
    figure.add_trace(
        go.Bar(
            x=data["Date"],
            y=data["Daily_Return"],
            name="Daily Return (%)",
            marker_color=bar_colors,
            hovertemplate="Date: %{x}<br>Return: %{y:.2f}%<extra></extra>",
        )
    )

    figure.update_layout(
        **CHART_LAYOUT,
        height=CHART_HEIGHT,
        title=dict(text=f"{symbol} — Daily Returns (%)", x=0.01),
        xaxis_title="Date",
        yaxis_title="Return (%)",
    )

    return figure


def create_moving_average_chart(frame: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create an interactive chart with close price and moving averages.

    Shows Close price alongside 7-day and 30-day simple moving averages.

    Args:
        frame: Processed history with Close, MA_7, MA_30 columns
        symbol: Stock ticker for the chart title

    Returns:
        Plotly Figure object
    """
    data = _prepare_chart_data(frame)

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Close"],
            mode="lines",
            name="Close Price",
            line=dict(color=COLOR_PRICE, width=2),
            hovertemplate="Close: $%{y:.2f}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["MA_7"],
            mode="lines",
            name=f"{MA_SHORT_PERIOD}-Day MA",
            line=dict(color=COLOR_MA_SHORT, width=1.5, dash="dot"),
            hovertemplate=f"{MA_SHORT_PERIOD}-Day MA: $%{{y:.2f}}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["MA_30"],
            mode="lines",
            name=f"{MA_LONG_PERIOD}-Day MA",
            line=dict(color=COLOR_MA_LONG, width=1.5, dash="dash"),
            hovertemplate=f"{MA_LONG_PERIOD}-Day MA: $%{{y:.2f}}<extra></extra>",
        )
    )

    figure.update_layout(
        **CHART_LAYOUT,
        height=CHART_HEIGHT,
        title=dict(text=f"{symbol} — Price & Moving Averages", x=0.01),
        xaxis_title="Date",
        yaxis_title="Price (USD)",
    )

    return figure


def create_combined_price_volume_chart(frame: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create a combined price + volume chart with two subplots.

    Bonus chart: candlestick on top, volume bars below (shared x-axis).

    Args:
        frame: Processed history with full OHLCV data
        symbol: Stock ticker for the chart title

    Returns:
        Plotly Figure with two subplots
    """
    data = _prepare_chart_data(frame)

    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
        subplot_titles=(f"{symbol} Price", "Volume"),
    )

    figure.add_trace(
        go.Candlestick(
            x=data["Date"],
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="OHLC",
            increasing_line_color=COLOR_UP,
            decreasing_line_color=COLOR_DOWN,
        ),
        row=1,
        col=1,
    )

    bar_colors = [
        COLOR_UP if close >= open else COLOR_DOWN
        for close, open in zip(data["Close"], data["Open"])
    ]
    figure.add_trace(
        go.Bar(
            x=data["Date"],
            y=data["Volume"],
            name="Volume",
            marker_color=bar_colors,
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    figure.update_layout(
        template="plotly_white",
        height=600,
        hovermode="x unified",
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis_rangeslider_visible=False,
        title=dict(text=f"{symbol} — Price & Volume Overview", x=0.01),
    )
    figure.update_yaxes(title_text="Price (USD)", row=1, col=1)
    figure.update_yaxes(title_text="Volume", row=2, col=1)

    return figure
