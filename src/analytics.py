"""
Analytics calculations for the Stock Market Dashboard.

Uses Pandas to compute period-level statistics:
    - Highest price
    - Lowest price
    - Average closing price
    - Volatility
    - Total trading volume
"""

from __future__ import annotations

from typing import TypedDict

import pandas as pd

from src.exceptions import EmptyDataError


class AnalyticsSummary(TypedDict):
    """Dictionary shape for period analytics results."""

    highest_price: float
    highest_price_date: str
    lowest_price: float
    lowest_price_date: str
    average_close: float
    volatility: float
    total_volume: int
    trading_days: int


def _format_date(date_value: pd.Timestamp) -> str:
    """Format a timestamp as a readable date string."""
    return pd.to_datetime(date_value).strftime("%Y-%m-%d")


def calculate_highest_price(frame: pd.DataFrame) -> tuple[float, str]:
    """
    Find the highest price and the date it occurred.

    Uses the 'High' column (intraday peak per trading day).

    Args:
        frame: Processed history DataFrame

    Returns:
        Tuple of (highest price, date string)
    """
    highest_index = frame["High"].idxmax()
    highest_row = frame.loc[highest_index]
    return round(float(highest_row["High"]), 2), _format_date(highest_row["Date"])


def calculate_lowest_price(frame: pd.DataFrame) -> tuple[float, str]:
    """
    Find the lowest price and the date it occurred.

    Uses the 'Low' column (intraday bottom per trading day).

    Args:
        frame: Processed history DataFrame

    Returns:
        Tuple of (lowest price, date string)
    """
    lowest_index = frame["Low"].idxmin()
    lowest_row = frame.loc[lowest_index]
    return round(float(lowest_row["Low"]), 2), _format_date(lowest_row["Date"])


def calculate_average_close(frame: pd.DataFrame) -> float:
    """
    Calculate the average closing price over the selected period.

    Args:
        frame: Processed history DataFrame with Close column

    Returns:
        Mean closing price rounded to 2 decimal places
    """
    return round(float(frame["Close"].mean()), 2)


def calculate_volatility(frame: pd.DataFrame) -> float:
    """
    Calculate price volatility as the standard deviation of daily returns.

    Uses the pre-computed Daily_Return column (%).
    Higher value = more price fluctuation over the period.

    Args:
        frame: Processed history with Daily_Return column

    Returns:
        Volatility (std dev of daily returns) as a percentage
    """
    # Need at least 2 data points for a meaningful std deviation
    if len(frame) < 2:
        return 0.0

    daily_std = frame["Daily_Return"].std()
    return round(float(daily_std), 2)


def calculate_total_volume(frame: pd.DataFrame) -> int:
    """
    Sum all trading volume over the selected period.

    Args:
        frame: Processed history with Volume column

    Returns:
        Total volume as an integer
    """
    return int(frame["Volume"].sum())


def calculate_analytics(frame: pd.DataFrame) -> AnalyticsSummary:
    """
    Run all analytics calculations on processed stock history.

    Args:
        frame: Processed history DataFrame from data_processor

    Returns:
        AnalyticsSummary with all period statistics

    Raises:
        EmptyDataError: If the DataFrame has no rows
    """
    if frame is None or frame.empty:
        raise EmptyDataError("No data available to calculate analytics.")

    highest_price, highest_date = calculate_highest_price(frame)
    lowest_price, lowest_date = calculate_lowest_price(frame)

    return AnalyticsSummary(
        highest_price=highest_price,
        highest_price_date=highest_date,
        lowest_price=lowest_price,
        lowest_price_date=lowest_date,
        average_close=calculate_average_close(frame),
        volatility=calculate_volatility(frame),
        total_volume=calculate_total_volume(frame),
        trading_days=len(frame),
    )
