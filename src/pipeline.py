"""
Unified data pipeline for the Stock Market Dashboard.

Connects all backend modules into a single end-to-end flow:

    Module 2 (data_fetcher)  →  fetch live stock data
    Module 3 (data_processor) →  clean & calculate indicators
    Module 6 (analytics)      →  compute period statistics

This is the central integration point used by the dashboard layout.
"""

from __future__ import annotations

from typing import TypedDict

from src.analytics import AnalyticsSummary, calculate_analytics
from src.data_fetcher import fetch_stock_quote
from src.data_processor import ProcessedStockData, process_stock_data


class DashboardData(TypedDict):
    """Complete integrated dataset ready for the full dashboard UI."""

    processed: ProcessedStockData
    analytics: AnalyticsSummary


def load_dashboard_data(symbol: str, date_range: str) -> DashboardData:
    """
    Run the full integrated data pipeline for a stock symbol.

    Pipeline steps:
        1. Fetch raw quote + history  (data_fetcher)
        2. Clean data & indicators    (data_processor)
        3. Calculate period analytics (analytics)

    Args:
        symbol: Stock ticker (e.g., 'AAPL')
        date_range: Historical window (e.g., '1mo', '3mo')

    Returns:
        DashboardData with processed stock data and analytics

    Raises:
        InvalidSymbolError, EmptyDataError, ConnectionError,
        RateLimitError, APIError — propagated from underlying modules
    """
    # Step 1: Fetch live/near-real-time data (Module 2)
    quote = fetch_stock_quote(symbol, date_range=date_range)

    # Step 2: Clean and compute indicators (Module 3)
    processed = process_stock_data(quote)

    # Step 3: Calculate period analytics (Module 6)
    analytics = calculate_analytics(processed["history"])

    return DashboardData(
        processed=processed,
        analytics=analytics,
    )
