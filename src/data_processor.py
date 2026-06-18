"""
Data processing module for the Stock Market Dashboard.

Uses Pandas to clean raw stock data and calculate financial indicators
including moving averages and daily returns.

Functions:
    - clean_stock_data()
    - add_moving_averages()
    - add_daily_returns()
    - calculate_indicators()
    - process_stock_data()
"""

from __future__ import annotations

from typing import Any, TypedDict

import pandas as pd

from config.settings import MA_LONG_PERIOD, MA_SHORT_PERIOD, REQUIRED_HISTORY_COLUMNS
from src.exceptions import EmptyDataError


class StockIndicators(TypedDict):
    """Dictionary shape for calculated financial indicators."""

    current_price: float
    open_price: float
    high: float
    low: float
    previous_close: float
    volume: int
    daily_change_pct: float
    ma_7: float | None
    ma_30: float | None


class ProcessedStockData(TypedDict):
    """Full output from the data processing pipeline."""

    symbol: str
    history: pd.DataFrame
    indicators: StockIndicators
    date_range: str
    data_source: str


def clean_stock_data(frame: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize raw OHLCV stock history data.

    Steps:
        1. Validate required columns exist
        2. Convert Date to datetime and sort ascending
        3. Convert price/volume columns to numeric
        4. Remove duplicate dates and rows with missing prices
        5. Fill missing volume values with 0

    Args:
        frame: Raw historical DataFrame from the data fetcher

    Returns:
        Cleaned DataFrame ready for calculations

    Raises:
        EmptyDataError: Input is empty or has no usable rows after cleaning
    """
    if frame is None or frame.empty:
        raise EmptyDataError("No stock data available to process.")

    cleaned = frame.copy()

    # Normalize column names (handles APIs that return lowercase names)
    cleaned.columns = [str(col).strip() for col in cleaned.columns]

    column_map = {
        "date": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    }
    cleaned = cleaned.rename(columns=column_map)

    missing_columns = [
        column for column in REQUIRED_HISTORY_COLUMNS if column not in cleaned.columns
    ]
    if missing_columns:
        raise EmptyDataError(
            f"Stock data is missing required columns: {', '.join(missing_columns)}"
        )

    # Keep only the columns needed for dashboard calculations
    cleaned = cleaned[REQUIRED_HISTORY_COLUMNS].copy()

    # Convert Date column and sort oldest -> newest
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce", utc=True)
    cleaned = cleaned.dropna(subset=["Date"])

    # Convert numeric columns; invalid values become NaN
    for column in ["Open", "High", "Low", "Close", "Volume"]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    # Remove rows without valid OHLC prices
    cleaned = cleaned.dropna(subset=["Open", "High", "Low", "Close"])

    # Replace missing volume with zero (weekends/holidays may have gaps)
    cleaned["Volume"] = cleaned["Volume"].fillna(0).astype(int)

    # Remove duplicate trading dates (keep the latest row per date)
    cleaned = cleaned.drop_duplicates(subset=["Date"], keep="last")

    # Sort chronologically for time-series calculations
    cleaned = cleaned.sort_values("Date").reset_index(drop=True)

    if cleaned.empty:
        raise EmptyDataError("No usable stock data remains after cleaning.")

    return cleaned


def add_moving_averages(
    frame: pd.DataFrame,
    short_period: int = MA_SHORT_PERIOD,
    long_period: int = MA_LONG_PERIOD,
) -> pd.DataFrame:
    """
    Add 7-day and 30-day simple moving averages to the DataFrame.

    Uses Pandas rolling mean on the Close price column.

    Args:
        frame: Cleaned stock history DataFrame
        short_period: Short moving average window (default 7 days)
        long_period: Long moving average window (default 30 days)

    Returns:
        DataFrame with MA_7 and MA_30 columns added
    """
    processed = frame.copy()

    # Simple moving average = rolling mean of closing prices
    processed["MA_7"] = (
        processed["Close"].rolling(window=short_period, min_periods=1).mean()
    )
    processed["MA_30"] = (
        processed["Close"].rolling(window=long_period, min_periods=1).mean()
    )

    return processed


def add_daily_returns(frame: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily percentage returns based on closing prices.

    Formula: ((Close_today - Close_yesterday) / Close_yesterday) * 100

    Args:
        frame: DataFrame with a Close column

    Returns:
        DataFrame with Daily_Return column added (%)
    """
    processed = frame.copy()

    # pct_change() computes percent change between consecutive rows
    processed["Daily_Return"] = processed["Close"].pct_change() * 100

    # First row has no previous close, so return is 0
    processed["Daily_Return"] = processed["Daily_Return"].fillna(0).round(4)

    return processed


def calculate_daily_change_percent(
    current_price: float,
    previous_close: float,
) -> float:
    """
    Calculate daily price change as a percentage.

    Args:
        current_price: Latest trading price
        previous_close: Previous session closing price

    Returns:
        Daily change percentage rounded to 2 decimal places
    """
    if previous_close == 0:
        return 0.0

    change_pct = ((current_price - previous_close) / previous_close) * 100
    return round(change_pct, 2)


def calculate_indicators(
    frame: pd.DataFrame,
    quote: dict[str, Any],
) -> StockIndicators:
    """
    Calculate and return all financial indicators for the dashboard.

    Combines live quote data with processed historical DataFrame values.

    Args:
        frame: Processed history with MA and Daily_Return columns
        quote: Quote dictionary from fetch_stock_quote()

    Returns:
        StockIndicators dictionary with all required metrics
    """
    if frame.empty:
        raise EmptyDataError("Cannot calculate indicators from empty data.")

    latest_row = frame.iloc[-1]

    current_price = float(quote.get("current_price", latest_row["Close"]))
    open_price = float(quote.get("open_price", latest_row["Open"]))
    day_high = float(quote.get("day_high", latest_row["High"]))
    day_low = float(quote.get("day_low", latest_row["Low"]))
    previous_close = float(quote.get("previous_close", frame.iloc[-2]["Close"] if len(frame) > 1 else latest_row["Close"]))
    volume = int(quote.get("volume", latest_row["Volume"]))

    # Use latest moving average values from the processed DataFrame
    ma_7 = round(float(latest_row["MA_7"]), 2) if pd.notna(latest_row["MA_7"]) else None
    ma_30 = round(float(latest_row["MA_30"]), 2) if pd.notna(latest_row["MA_30"]) else None

    daily_change_pct = calculate_daily_change_percent(current_price, previous_close)

    return StockIndicators(
        current_price=round(current_price, 2),
        open_price=round(open_price, 2),
        high=round(day_high, 2),
        low=round(day_low, 2),
        previous_close=round(previous_close, 2),
        volume=volume,
        daily_change_pct=daily_change_pct,
        ma_7=ma_7,
        ma_30=ma_30,
    )


def process_stock_data(quote: dict[str, Any]) -> ProcessedStockData:
    """
    Run the full data processing pipeline on a fetched stock quote.

    Pipeline:
        1. Clean raw history data
        2. Add moving averages (7-day and 30-day)
        3. Add daily returns
        4. Calculate financial indicators

    Args:
        quote: Output dictionary from fetch_stock_quote()

    Returns:
        ProcessedStockData with cleaned history and indicators

    Raises:
        EmptyDataError: Quote has no processable history
    """
    raw_history = quote.get("history")

    if raw_history is None or raw_history.empty:
        raise EmptyDataError("Fetched quote does not contain historical data.")

    # Step 1: Clean the raw data
    cleaned = clean_stock_data(raw_history)

    # Step 2: Add technical indicator columns
    with_ma = add_moving_averages(cleaned)

    # Step 3: Add daily return column
    processed_history = add_daily_returns(with_ma)

    # Step 4: Build indicator summary cards
    indicators = calculate_indicators(processed_history, quote)

    return ProcessedStockData(
        symbol=str(quote.get("symbol", "UNKNOWN")),
        history=processed_history,
        indicators=indicators,
        date_range=str(quote.get("date_range", "")),
        data_source=str(quote.get("data_source", "Unknown")),
    )
