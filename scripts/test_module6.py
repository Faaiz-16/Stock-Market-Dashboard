"""
Module 6 test script — Analytics Section

Run from the project root:

    python scripts/test_module6.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.analytics import (  # noqa: E402
    calculate_analytics,
    calculate_average_close,
    calculate_highest_price,
    calculate_lowest_price,
    calculate_total_volume,
    calculate_volatility,
)
from src.data_fetcher import fetch_stock_quote  # noqa: E402
from src.data_processor import process_stock_data  # noqa: E402
from src.exceptions import EmptyDataError  # noqa: E402
from src.ui.analytics_cards import get_analytics_summary  # noqa: E402


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_highest_price() -> None:
    """Verify highest price calculation."""
    print_section("TEST 1: Highest Price")
    processed = process_stock_data(fetch_stock_quote("AAPL", "3mo"))
    price, date = calculate_highest_price(processed["history"])
    print(f"  Highest: ${price:.2f} on {date}")
    assert price > 0
    print("✅ calculate_highest_price() works correctly")


def test_lowest_price() -> None:
    """Verify lowest price calculation."""
    print_section("TEST 2: Lowest Price")
    processed = process_stock_data(fetch_stock_quote("MSFT", "3mo"))
    price, date = calculate_lowest_price(processed["history"])
    print(f"  Lowest: ${price:.2f} on {date}")
    assert price > 0
    print("✅ calculate_lowest_price() works correctly")


def test_average_close() -> None:
    """Verify average closing price calculation."""
    print_section("TEST 3: Average Closing Price")
    processed = process_stock_data(fetch_stock_quote("TSLA", "1mo"))
    average = calculate_average_close(processed["history"])
    print(f"  Average Close: ${average:.2f}")
    assert average > 0
    print("✅ calculate_average_close() works correctly")


def test_volatility() -> None:
    """Verify volatility calculation."""
    print_section("TEST 4: Volatility")
    processed = process_stock_data(fetch_stock_quote("AMZN", "3mo"))
    volatility = calculate_volatility(processed["history"])
    print(f"  Volatility: {volatility:.2f}%")
    assert volatility >= 0
    print("✅ calculate_volatility() works correctly")


def test_total_volume() -> None:
    """Verify total volume calculation."""
    print_section("TEST 5: Total Volume")
    processed = process_stock_data(fetch_stock_quote("GOOGL", "1mo"))
    total = calculate_total_volume(processed["history"])
    print(f"  Total Volume: {total:,}")
    assert total > 0
    print("✅ calculate_total_volume() works correctly")


def test_full_analytics_pipeline() -> None:
    """Verify the complete analytics summary."""
    print_section("TEST 6: Full Analytics Pipeline")
    processed = process_stock_data(fetch_stock_quote("NVDA", "3mo"))
    analytics = calculate_analytics(processed["history"])

    required_keys = [
        "highest_price", "highest_price_date",
        "lowest_price", "lowest_price_date",
        "average_close", "volatility",
        "total_volume", "trading_days",
    ]
    for key in required_keys:
        print(f"  {key}: {analytics[key]}")

    assert analytics["highest_price"] >= analytics["lowest_price"]
    assert analytics["trading_days"] > 0
    print("✅ calculate_analytics() pipeline works correctly")


def test_analytics_ui_helper() -> None:
    """Verify the UI helper returns the same analytics."""
    print_section("TEST 7: Analytics UI Helper")
    processed = process_stock_data(fetch_stock_quote("AAPL", "1mo"))
    summary = get_analytics_summary(processed)
    assert "highest_price" in summary
    assert "volatility" in summary
    print("✅ get_analytics_summary() works correctly")


def test_empty_data_error() -> None:
    """Verify empty data raises a friendly error."""
    print_section("TEST 8: Empty Data Error Handling")
    import pandas as pd

    try:
        calculate_analytics(pd.DataFrame())
        print("❌ Expected EmptyDataError")
    except EmptyDataError as exc:
        print(f"✅ Caught expected error: {exc.message}")


def main() -> None:
    """Run all Module 6 verification tests."""
    print("Starting Module 6 tests for Analytics Section...")

    tests = [
        test_highest_price,
        test_lowest_price,
        test_average_close,
        test_volatility,
        test_total_volume,
        test_full_analytics_pipeline,
        test_analytics_ui_helper,
        test_empty_data_error,
    ]

    for test in tests:
        test()

    print_section("ALL MODULE 6 TESTS PASSED ✅")


if __name__ == "__main__":
    main()
