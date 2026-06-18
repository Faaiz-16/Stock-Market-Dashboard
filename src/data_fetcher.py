"""
Stock data fetching module.

Uses the Requests library to fetch near real-time and historical
stock data from public financial APIs.

Primary source:  EOD Historical Data (free demo token included)
Fallback source: Yahoo Finance (when EOD is unavailable)

Functions:
    - normalize_symbol()
    - search_stocks()
    - fetch_stock_history()
    - fetch_stock_quote()
    - get_user_friendly_error()
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd
import requests

# curl_cffi impersonates a real browser so Yahoo Finance does not
# return HTTP 429 for symbols like GOOGL and NVDA.
try:
    from curl_cffi import requests as curl_requests

    CURL_CFFI_AVAILABLE = True
except ImportError:
    curl_requests = None  # type: ignore[assignment]
    CURL_CFFI_AVAILABLE = False

from config.settings import (
    DEFAULT_DATE_RANGE,
    DEFAULT_INTERVAL,
    EOD_API_TOKEN,
    EOD_BASE_URL,
    EOD_DEMO_TOKEN,
    EOD_DEMO_UNSUPPORTED,
    KNOWN_STOCKS,
    MAX_API_RETRIES,
    MAX_SEARCH_RESULTS,
    REQUEST_HEADERS,
    REQUEST_TIMEOUT_SECONDS,
    RETRY_DELAY_SECONDS,
    VALID_DATE_RANGES,
    YAHOO_CHART_URL,
    YAHOO_SEARCH_URL,
)
from src.exceptions import (
    APIError,
    ConnectionError,
    EmptyDataError,
    InvalidSymbolError,
    RateLimitError,
    StockDashboardError,
)

# Reuse one session for Yahoo Finance fallback calls
_yahoo_session: Any = None


def normalize_symbol(symbol: str) -> str:
    """
    Clean and standardize a stock symbol for API requests.

    Args:
        symbol: Raw user input (e.g., ' aapl ', 'MSFT')

    Returns:
        Uppercase trimmed symbol (e.g., 'AAPL')
    """
    return symbol.strip().upper()


def _range_to_days(date_range: str) -> int | None:
    """
    Convert a range string into an approximate day count.

    Returns None for 'max' (use a long default window).
    """
    mapping = {
        "1d": 1,
        "5d": 5,
        "1mo": 30,
        "3mo": 90,
        "6mo": 180,
        "1y": 365,
        "2y": 730,
        "5y": 1825,
    }
    return mapping.get(date_range)


def _date_range_to_bounds(date_range: str) -> tuple[str, str]:
    """Convert a dashboard date range into EOD API from/to dates (YYYY-MM-DD)."""
    days = _range_to_days(date_range)
    end_date = datetime.now(timezone.utc).date()

    if days is None:
        start_date = end_date - timedelta(days=3650)  # ~10 years for "max"
    else:
        start_date = end_date - timedelta(days=days)

    return start_date.isoformat(), end_date.isoformat()


def _request_with_error_handling(
    url: str,
    params: dict[str, Any] | None = None,
    session: requests.Session | None = None,
) -> requests.Response:
    """
    Perform an HTTP GET request with shared network error handling.

    Args:
        url: Endpoint URL
        params: Optional query parameters
        session: Optional Requests session

    Returns:
        Response object

    Raises:
        ConnectionError, APIError
    """
    client = session or requests

    try:
        response = client.get(
            url,
            params=params,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.exceptions.Timeout as exc:
        raise ConnectionError(
            "Request timed out. Please check your internet connection and try again."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise ConnectionError(
            "Unable to connect to the internet. Please check your network and try again."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise APIError(f"An unexpected request error occurred: {exc}") from exc

    return response


def _fetch_history_eod(symbol: str, date_range: str) -> pd.DataFrame:
    """
    Fetch historical OHLCV data from EOD Historical Data API.

    Uses the free demo token by default (no signup required).
    """
    from_date, to_date = _date_range_to_bounds(date_range)
    url = f"{EOD_BASE_URL}/eod/{symbol}.US"
    params = {
        "api_token": EOD_API_TOKEN,
        "fmt": "json",
        "from": from_date,
        "to": to_date,
    }

    response = _request_with_error_handling(url, params=params)

    if response.status_code in {401, 403}:
        raise InvalidSymbolError(
            f"Invalid stock symbol '{symbol}'. Please check the symbol and try again."
        )

    if response.status_code == 429:
        raise RateLimitError(
            "API rate limit reached. Please wait a moment and try again."
        )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise APIError(
            f"API request failed with status {response.status_code}. "
            "Please try again later."
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise APIError("API returned an invalid response. Please try again later.") from exc

    if not isinstance(payload, list) or not payload:
        raise EmptyDataError(
            f"No historical data available for '{symbol}' in the selected period."
        )

    frame = pd.DataFrame(payload)
    frame = frame.rename(
        columns={
            "date": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
    )

    required_columns = {"Date", "Open", "High", "Low", "Close", "Volume"}
    if not required_columns.issubset(frame.columns):
        raise APIError("API returned unexpected data format.")

    frame["Date"] = pd.to_datetime(frame["Date"], utc=True)
    frame = frame.dropna(subset=["Open", "High", "Low", "Close"]).reset_index(drop=True)

    if frame.empty:
        raise EmptyDataError(
            f"No usable price data found for '{symbol}' in the selected period."
        )

    return frame


def _fetch_realtime_eod(symbol: str) -> dict[str, Any]:
    """Fetch near real-time quote data from EOD Historical Data API."""
    url = f"{EOD_BASE_URL}/real-time/{symbol}.US"
    params = {"api_token": EOD_API_TOKEN, "fmt": "json"}

    response = _request_with_error_handling(url, params=params)

    if response.status_code in {401, 403}:
        raise InvalidSymbolError(
            f"Invalid stock symbol '{symbol}'. Please check the symbol and try again."
        )

    if response.status_code == 429:
        raise RateLimitError(
            "API rate limit reached. Please wait a moment and try again."
        )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise APIError(
            f"API request failed with status {response.status_code}. "
            "Please try again later."
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise APIError("API returned an invalid response. Please try again later.") from exc

    if not isinstance(payload, dict) or "close" not in payload:
        raise EmptyDataError(f"No quote data available for '{symbol}'.")

    return {
        "symbol": symbol,
        "currency": "USD",
        "exchange": "US",
        "current_price": float(payload.get("close", 0)),
        "previous_close": float(payload.get("previousClose", payload.get("close", 0))),
        "open_price": float(payload.get("open", payload.get("close", 0))),
        "day_high": float(payload.get("high", payload.get("close", 0))),
        "day_low": float(payload.get("low", payload.get("close", 0))),
        "volume": int(payload.get("volume", 0)),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "EOD Historical Data",
    }


def _get_yahoo_session() -> Any:
    """
    Return a session for Yahoo Finance API calls.

    Uses curl_cffi with Chrome impersonation when available — this avoids
    the HTTP 429 rate limits that plain requests triggers for GOOGL/NVDA.
    Falls back to a standard requests.Session otherwise.
    """
    global _yahoo_session

    if _yahoo_session is None:
        if CURL_CFFI_AVAILABLE:
            _yahoo_session = curl_requests.Session(impersonate="chrome")
        else:
            _yahoo_session = requests.Session()

        _yahoo_session.headers.update(REQUEST_HEADERS)

    return _yahoo_session


def _should_skip_eod(symbol: str) -> bool:
    """
    Check if a symbol should skip EOD and use Yahoo directly.

    The EOD demo token blocks certain popular tickers (returns 403)
    even though they are valid symbols like GOOGL and NVDA.
    """
    using_demo_token = EOD_API_TOKEN == EOD_DEMO_TOKEN
    return using_demo_token and symbol in EOD_DEMO_UNSUPPORTED


def _make_yahoo_api_request(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Send a GET request to Yahoo Finance with retry logic.

    Uses curl_cffi browser impersonation to avoid rate limits on
    symbols not covered by the EOD demo token (GOOGL, NVDA, etc.).
    """
    session = _get_yahoo_session()
    last_rate_limit_error: RateLimitError | None = None

    for attempt in range(1, MAX_API_RETRIES + 1):
        response = _request_with_error_handling(url, params=params, session=session)

        if response.status_code == 429:
            last_rate_limit_error = RateLimitError(
                "API rate limit reached. Please wait a moment and try again."
            )
            if attempt < MAX_API_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
                # Reset session so the next attempt gets a fresh connection
                global _yahoo_session
                _yahoo_session = None
                session = _get_yahoo_session()
                continue
            raise last_rate_limit_error

        if response.status_code == 404:
            symbol = url.split("/chart/")[-1] if "/chart/" in url else "unknown"
            raise InvalidSymbolError(
                f"Invalid stock symbol '{symbol}'. Please check the symbol and try again."
            )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise APIError(
                f"API request failed with status {response.status_code}. "
                "Please try again later."
            ) from exc

        try:
            return response.json()
        except ValueError as exc:
            raise APIError(
                "API returned an invalid response. Please try again later."
            ) from exc

    if last_rate_limit_error:
        raise last_rate_limit_error
    raise APIError("API request failed after multiple attempts.")


def search_stocks_local(query: str) -> list[dict[str, str]]:
    """
    Search the built-in stock list by symbol or company name.

    Used as the primary search method (fast and reliable).
    """
    cleaned_query = query.strip().lower()
    results: list[dict[str, str]] = []

    for symbol, company_name in KNOWN_STOCKS.items():
        symbol_match = cleaned_query in symbol.lower()
        name_match = cleaned_query in company_name.lower()

        if symbol_match or name_match:
            results.append(
                {
                    "symbol": symbol,
                    "name": company_name,
                    "exchange": "US",
                }
            )

    return results[:MAX_SEARCH_RESULTS]


def search_stocks(query: str) -> list[dict[str, str]]:
    """
    Search for stock symbols matching a user query.

    Tries local search first, then Yahoo Finance API as a bonus source.
    """
    cleaned_query = query.strip()

    if not cleaned_query:
        raise EmptyDataError("Please enter a search term to find stocks.")

    # Primary: fast local search against known stocks
    local_results = search_stocks_local(cleaned_query)
    if local_results:
        return local_results

    # Secondary: Yahoo remote search for symbols outside the local list
    params = {
        "q": cleaned_query,
        "quotesCount": MAX_SEARCH_RESULTS,
        "newsCount": 0,
        "enableFuzzyQuery": True,
    }

    try:
        data = _make_yahoo_api_request(YAHOO_SEARCH_URL, params=params)
    except (RateLimitError, APIError, ConnectionError):
        raise EmptyDataError(
            f"No stocks found for '{cleaned_query}'. Try another symbol or company name."
        ) from None

    quotes = data.get("quotes", [])
    results: list[dict[str, str]] = []

    for quote in quotes:
        symbol = quote.get("symbol")
        if not symbol:
            continue

        results.append(
            {
                "symbol": str(symbol).upper(),
                "name": str(quote.get("shortname") or quote.get("longname") or "Unknown"),
                "exchange": str(quote.get("exchange") or "N/A"),
            }
        )

    if not results:
        raise EmptyDataError(
            f"No stocks found for '{cleaned_query}'. Try another symbol or company name."
        )

    return results[:MAX_SEARCH_RESULTS]


def _parse_yahoo_chart_response(
    data: dict[str, Any],
    symbol: str,
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Parse Yahoo Finance chart JSON into quote metadata and a DataFrame."""
    chart = data.get("chart", {})
    error_info = chart.get("error")

    if error_info:
        description = error_info.get("description", "Unknown symbol")
        raise InvalidSymbolError(
            f"Invalid stock symbol '{symbol}'. {description}"
        )

    results = chart.get("result")
    if not results:
        raise InvalidSymbolError(
            f"Invalid stock symbol '{symbol}'. Please check the symbol and try again."
        )

    result = results[0]
    meta = result.get("meta", {})
    timestamps = result.get("timestamp", [])
    indicators = result.get("indicators", {}).get("quote", [{}])[0]

    if not timestamps:
        raise EmptyDataError(
            f"No historical data available for '{symbol}' in the selected period."
        )

    frame = pd.DataFrame(
        {
            "Date": pd.to_datetime(timestamps, unit="s", utc=True),
            "Open": indicators.get("open", []),
            "High": indicators.get("high", []),
            "Low": indicators.get("low", []),
            "Close": indicators.get("close", []),
            "Volume": indicators.get("volume", []),
        }
    )

    frame = frame.dropna(subset=["Open", "High", "Low", "Close"]).reset_index(drop=True)

    if frame.empty:
        raise EmptyDataError(
            f"No usable price data found for '{symbol}' in the selected period."
        )

    quote = {
        "symbol": meta.get("symbol", symbol),
        "currency": meta.get("currency", "USD"),
        "exchange": meta.get("exchangeName", "N/A"),
        "current_price": meta.get("regularMarketPrice"),
        "previous_close": meta.get("chartPreviousClose") or meta.get("previousClose"),
        "open_price": meta.get("regularMarketOpen") or frame.iloc[-1]["Open"],
        "day_high": meta.get("regularMarketDayHigh") or frame.iloc[-1]["High"],
        "day_low": meta.get("regularMarketDayLow") or frame.iloc[-1]["Low"],
        "volume": meta.get("regularMarketVolume") or frame.iloc[-1]["Volume"],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "data_source": "Yahoo Finance",
    }

    return quote, frame


def _fetch_history_yahoo(
    symbol: str,
    date_range: str,
    interval: str = DEFAULT_INTERVAL,
) -> pd.DataFrame:
    """Fetch historical data from Yahoo Finance (fallback source)."""
    url = YAHOO_CHART_URL.format(symbol=symbol)
    params = {"interval": interval, "range": date_range}
    data = _make_yahoo_api_request(url, params=params)
    _, history = _parse_yahoo_chart_response(data, symbol)
    return history


def _fetch_quote_yahoo(symbol: str, date_range: str) -> dict[str, Any]:
    """Fetch quote and history from Yahoo Finance (fallback source)."""
    url = YAHOO_CHART_URL.format(symbol=symbol)
    params = {"interval": DEFAULT_INTERVAL, "range": date_range}
    data = _make_yahoo_api_request(url, params=params)
    quote, history = _parse_yahoo_chart_response(data, symbol)

    return {
        **quote,
        "history": history,
        "date_range": date_range,
    }


def fetch_stock_history(
    symbol: str,
    date_range: str = DEFAULT_DATE_RANGE,
    interval: str = DEFAULT_INTERVAL,
) -> pd.DataFrame:
    """
    Fetch historical OHLCV stock data for charts and analytics.

    Tries EOD Historical Data first, then Yahoo Finance as fallback.
    """
    normalized_symbol = normalize_symbol(symbol)

    if not normalized_symbol:
        raise InvalidSymbolError("Stock symbol cannot be empty.")

    if date_range not in VALID_DATE_RANGES:
        raise APIError(
            f"Invalid date range '{date_range}'. "
            f"Choose one of: {', '.join(VALID_DATE_RANGES)}"
        )

    # Skip EOD for symbols blocked by the demo token (e.g. GOOGL, NVDA)
    if _should_skip_eod(normalized_symbol):
        return _fetch_history_yahoo(normalized_symbol, date_range, interval)

    try:
        return _fetch_history_eod(normalized_symbol, date_range)
    except (InvalidSymbolError, EmptyDataError, RateLimitError, APIError, ConnectionError):
        return _fetch_history_yahoo(normalized_symbol, date_range, interval)


def fetch_stock_quote(
    symbol: str,
    date_range: str = DEFAULT_DATE_RANGE,
) -> dict[str, Any]:
    """
    Fetch current quote details and recent history for a stock.

    Tries EOD Historical Data first, then Yahoo Finance as fallback.
    """
    normalized_symbol = normalize_symbol(symbol)

    if not normalized_symbol:
        raise InvalidSymbolError("Stock symbol cannot be empty.")

    # Skip EOD for symbols blocked by the demo token (e.g. GOOGL, NVDA)
    if _should_skip_eod(normalized_symbol):
        return _fetch_quote_yahoo(normalized_symbol, date_range)

    try:
        quote = _fetch_realtime_eod(normalized_symbol)
        history = _fetch_history_eod(normalized_symbol, date_range)

        return {
            **quote,
            "history": history,
            "date_range": date_range,
        }
    except (InvalidSymbolError, EmptyDataError, RateLimitError, APIError, ConnectionError):
        return _fetch_quote_yahoo(normalized_symbol, date_range)


def get_user_friendly_error(error: Exception) -> str:
    """
    Convert exceptions into messages safe to show in the Streamlit UI.

    Args:
        error: Any exception raised during data fetching

    Returns:
        Human-readable error string
    """
    if isinstance(error, StockDashboardError):
        return error.message

    return (
        "An unexpected error occurred while fetching stock data. "
        "Please try again later."
    )
