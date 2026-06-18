"""
Module 3 test script — Data Processing

Run from the project root:

    python scripts/test_module3.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_fetcher import fetch_stock_quote, get_user_friendly_error  # noqa: E402
from src.data_processor import (  # noqa: E402
    add_daily_returns,
    add_moving_averages,
    calculate_daily_change_percent,
    calculate_indicators,
    clean_stock_data,
    process_stock_data,
)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_clean_stock_data() -> None:
    """Verify data cleaning produces valid OHLCV rows."""
    print_section("TEST 1: Clean Stock Data")
    quote = fetch_stock_quote("AAPL", date_range="1mo")
    cleaned = clean_stock_data(quote["history"])
    print(f"Rows after cleaning: {len(cleaned)}")
    print(f"Columns: {list(cleaned.columns)}")
    assert list(cleaned.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
    print("✅ clean_stock_data() works correctly")


def test_moving_averages() -> None:
    """Verify 7-day and 30-day moving averages are calculated."""
    print_section("TEST 2: Moving Averages")
    quote = fetch_stock_quote("MSFT", date_range="3mo")
    cleaned = clean_stock_data(quote["history"])
    processed = add_moving_averages(cleaned)
    assert "MA_7" in processed.columns
    assert "MA_30" in processed.columns
    latest = processed.iloc[-1]
    print(f"Latest Close:  ${latest['Close']:.2f}")
    print(f"7-Day MA:      ${latest['MA_7']:.2f}")
    print(f"30-Day MA:     ${latest['MA_30']:.2f}")
    print("✅ add_moving_averages() works correctly")


def test_daily_returns() -> None:
    """Verify daily return percentages are calculated."""
    print_section("TEST 3: Daily Returns")
    quote = fetch_stock_quote("TSLA", date_range="1mo")
    cleaned = clean_stock_data(quote["history"])
    processed = add_daily_returns(cleaned)
    assert "Daily_Return" in processed.columns
    print(processed[["Date", "Close", "Daily_Return"]].tail(3).to_string(index=False))
    print("✅ add_daily_returns() works correctly")


def test_daily_change_percent() -> None:
    """Verify daily change percentage formula."""
    print_section("TEST 4: Daily Change Percentage")
    change = calculate_daily_change_percent(current_price=110.0, previous_close=100.0)
    assert change == 10.0
    print(f"Change from $100 -> $110: {change}%")
    print("✅ calculate_daily_change_percent() works correctly")


def test_calculate_indicators() -> None:
    """Verify all required financial indicators are produced."""
    print_section("TEST 5: Financial Indicators")
    quote = fetch_stock_quote("MSFT", date_range="3mo")
    cleaned = clean_stock_data(quote["history"])
    with_ma = add_moving_averages(cleaned)
    with_returns = add_daily_returns(with_ma)
    indicators = calculate_indicators(with_returns, quote)

    required_keys = [
        "current_price",
        "open_price",
        "high",
        "low",
        "previous_close",
        "volume",
        "daily_change_pct",
        "ma_7",
        "ma_30",
    ]
    for key in required_keys:
        print(f"  {key}: {indicators[key]}")

    assert all(key in indicators for key in required_keys)
    print("✅ calculate_indicators() works correctly")


def test_process_stock_data_pipeline() -> None:
    """Verify the full processing pipeline end-to-end."""
    print_section("TEST 6: Full Processing Pipeline")
    quote = fetch_stock_quote("TSLA", date_range="1mo")
    processed = process_stock_data(quote)

    print(f"Symbol:       {processed['symbol']}")
    print(f"Data Source:  {processed['data_source']}")
    print(f"History Rows: {len(processed['history'])}")
    print(f"History Cols: {list(processed['history'].columns)}")
    print(f"Current Price:${processed['indicators']['current_price']}")

    expected_columns = {
        "Date", "Open", "High", "Low", "Close", "Volume",
        "MA_7", "MA_30", "Daily_Return",
    }
    assert expected_columns.issubset(set(processed["history"].columns))
    print("✅ process_stock_data() pipeline works correctly")


def main() -> None:
    """Run all Module 3 verification tests."""
    print("Starting Module 3 tests for Data Processing...")

    tests = [
        test_clean_stock_data,
        test_moving_averages,
        test_daily_returns,
        test_daily_change_percent,
        test_calculate_indicators,
        test_process_stock_data_pipeline,
    ]

    for test in tests:
        try:
            test()
        except Exception as exc:
            print(f"❌ {test.__name__} failed: {get_user_friendly_error(exc)}")
            raise

    print_section("ALL MODULE 3 TESTS PASSED ✅")


if __name__ == "__main__":
    main()
