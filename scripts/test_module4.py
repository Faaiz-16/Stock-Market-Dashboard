"""
Module 4 test script — Dashboard UI helpers

Run from the project root:

    python scripts/test_module4.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DATE_RANGE_LABELS, DEFAULT_STOCKS, VALID_DATE_RANGES  # noqa: E402
from src.data_fetcher import fetch_stock_quote  # noqa: E402
from src.data_processor import process_stock_data  # noqa: E402
from src.ui.formatters import (  # noqa: E402
    format_change_percent,
    format_price,
    format_volume,
    get_change_delta,
)
from src.ui.sidebar import SidebarFilters  # noqa: E402


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_formatters() -> None:
    """Verify price, volume, and percentage formatters."""
    print_section("TEST 1: UI Formatters")
    assert format_price(1234.5) == "$1,234.50"
    assert format_price(None) == "N/A"
    assert format_volume(1_500_000) == "1,500,000"
    assert format_change_percent(2.5) == "+2.50%"
    assert format_change_percent(-1.2) == "-1.20%"
    assert get_change_delta(3.14) == "3.14%"
    print("✅ All formatters work correctly")


def test_date_range_labels() -> None:
    """Verify every valid date range has a human-readable label."""
    print_section("TEST 2: Date Range Labels")
    for date_range in VALID_DATE_RANGES:
        label = DATE_RANGE_LABELS.get(date_range)
        assert label is not None, f"Missing label for {date_range}"
        print(f"  {date_range} → {label}")
    print("✅ All date range labels defined")


def test_sidebar_filters_dataclass() -> None:
    """Verify SidebarFilters holds the expected filter values."""
    print_section("TEST 3: Sidebar Filters Model")
    filters = SidebarFilters(symbol="AAPL", date_range="1mo", refresh=True)
    assert filters.symbol == "AAPL"
    assert filters.date_range == "1mo"
    assert filters.refresh is True
    print(f"  Symbol: {filters.symbol}")
    print(f"  Range:  {filters.date_range}")
    print(f"  Refresh:{filters.refresh}")
    print("✅ SidebarFilters dataclass works correctly")


def test_default_stocks_available() -> None:
    """Verify all default stocks are configured."""
    print_section("TEST 4: Default Stock List")
    expected = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "NVDA"]
    assert DEFAULT_STOCKS == expected
    print(f"  Stocks: {', '.join(DEFAULT_STOCKS)}")
    print("✅ Default stock list is correct")


def test_statistics_cards_data() -> None:
    """Verify processed data has all fields needed by statistics cards."""
    print_section("TEST 5: Statistics Cards Data")
    quote = fetch_stock_quote("AAPL", date_range="1mo")
    processed = process_stock_data(quote)
    indicators = processed["indicators"]

    required_keys = [
        "current_price", "open_price", "high", "low",
        "previous_close", "volume", "daily_change_pct",
        "ma_7", "ma_30",
    ]
    for key in required_keys:
        assert key in indicators, f"Missing indicator: {key}"
        print(f"  {key}: {indicators[key]}")

    print("✅ All statistics card fields are available")


def test_ui_module_imports() -> None:
    """Verify all UI modules import without errors."""
    print_section("TEST 6: UI Module Imports")
    from src.ui import header, layout, sidebar, stats_cards, styles  # noqa: F401

    print("  header.py     ✅")
    print("  sidebar.py    ✅")
    print("  stats_cards.py✅")
    print("  layout.py     ✅")
    print("  styles.py     ✅")
    print("✅ All UI modules import successfully")


def main() -> None:
    """Run all Module 4 verification tests."""
    print("Starting Module 4 tests for Dashboard UI...")

    tests = [
        test_formatters,
        test_date_range_labels,
        test_sidebar_filters_dataclass,
        test_default_stocks_available,
        test_statistics_cards_data,
        test_ui_module_imports,
    ]

    for test in tests:
        test()

    print_section("ALL MODULE 4 TESTS PASSED ✅")


if __name__ == "__main__":
    main()
