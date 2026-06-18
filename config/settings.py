"""
Application settings and constants for the Stock Market Dashboard.

Centralizes API URLs, default stocks, and request configuration
so values are not hardcoded across the codebase.
"""

from typing import Final
import os

# ---------------------------------------------------------------------------
# Default stock symbols available in the dashboard
# ---------------------------------------------------------------------------
DEFAULT_STOCKS: Final[list[str]] = [
    "AAPL",
    "MSFT",
    "TSLA",
    "GOOGL",
    "AMZN",
    "NVDA",
]

# ---------------------------------------------------------------------------
# EOD Historical Data API (primary — reliable with free demo token)
# Get your own free key at: https://eodhistoricaldata.com/
# ---------------------------------------------------------------------------
EOD_BASE_URL: Final[str] = "https://eodhistoricaldata.com/api"
EOD_DEMO_TOKEN: Final[str] = "demo"
EOD_API_TOKEN: Final[str] = os.getenv("EOD_API_TOKEN", EOD_DEMO_TOKEN)

# Symbols not available on the EOD *demo* token (403 response).
# These are valid tickers — route them to Yahoo Finance when using demo.
EOD_DEMO_UNSUPPORTED: Final[set[str]] = {
    "GOOGL",
    "NVDA",
    "META",
    "NFLX",
    "AMD",
    "INTC",
    "IBM",
}

# ---------------------------------------------------------------------------
# Yahoo Finance public API endpoints (fallback when EOD is unavailable)
# Used with the Requests library for near real-time stock data
# ---------------------------------------------------------------------------
YAHOO_CHART_URL: Final[str] = (
    "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"
)
YAHOO_SEARCH_URL: Final[str] = (
    "https://query1.finance.yahoo.com/v1/finance/search"
)
YAHOO_WARMUP_URL: Final[str] = "https://finance.yahoo.com/"

# ---------------------------------------------------------------------------
# Valid date range options for historical data (Yahoo Finance "range" parameter)
# ---------------------------------------------------------------------------
VALID_DATE_RANGES: Final[list[str]] = [
    "1d",
    "5d",
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
    "5y",
    "max",
]

# Default range when none is specified
DEFAULT_DATE_RANGE: Final[str] = "1mo"

# Human-readable labels for date range dropdown
DATE_RANGE_LABELS: Final[dict[str, str]] = {
    "1d": "1 Day",
    "5d": "5 Days",
    "1mo": "1 Month",
    "3mo": "3 Months",
    "6mo": "6 Months",
    "1y": "1 Year",
    "2y": "2 Years",
    "5y": "5 Years",
    "max": "All Time",
}

# Candlestick interval (daily data for dashboard charts)
DEFAULT_INTERVAL: Final[str] = "1d"

# ---------------------------------------------------------------------------
# HTTP request settings
# ---------------------------------------------------------------------------
REQUEST_TIMEOUT_SECONDS: Final[int] = 15

# Browser-like headers help avoid blocked requests from some APIs
REQUEST_HEADERS: Final[dict[str, str]] = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# Maximum search results returned to the user
MAX_SEARCH_RESULTS: Final[int] = 10

# Retry settings for transient API failures (e.g., rate limits)
MAX_API_RETRIES: Final[int] = 3
RETRY_DELAY_SECONDS: Final[float] = 3.0

# ---------------------------------------------------------------------------
# Known stocks for local symbol search (fallback when search API is limited)
# ---------------------------------------------------------------------------
KNOWN_STOCKS: Final[dict[str, str]] = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "TSLA": "Tesla Inc.",
    "GOOGL": "Alphabet Inc. (Google)",
    "AMZN": "Amazon.com Inc.",
    "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms Inc.",
    "NFLX": "Netflix Inc.",
    "AMD": "Advanced Micro Devices Inc.",
    "INTC": "Intel Corporation",
    "IBM": "International Business Machines",
    "ORCL": "Oracle Corporation",
    "CRM": "Salesforce Inc.",
    "UBER": "Uber Technologies Inc.",
    "DIS": "The Walt Disney Company",
    "BA": "Boeing Company",
    "JPM": "JPMorgan Chase & Co.",
    "V": "Visa Inc.",
    "MA": "Mastercard Inc.",
    "WMT": "Walmart Inc.",
}

# ---------------------------------------------------------------------------
# Technical indicator settings (used in Module 3 data processing)
# ---------------------------------------------------------------------------
MA_SHORT_PERIOD: Final[int] = 7
MA_LONG_PERIOD: Final[int] = 30

# Required OHLCV columns for processed stock history
REQUIRED_HISTORY_COLUMNS: Final[list[str]] = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]
