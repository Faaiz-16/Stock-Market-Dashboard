"""
Module 2 test script — Stock Data Fetching

Run from the project root to verify API integration without Streamlit:

    python scripts/test_module2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow imports from the project root when running this script directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_fetcher import (  # noqa: E402
    fetch_stock_history,
    fetch_stock_quote,
    get_user_friendly_error,
    normalize_symbol,
    search_stocks,
    search_stocks_local,
)
from src.exceptions import InvalidSymbolError  # noqa: E402


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_symbol_normalization() -> None:
    """Verify symbol cleaning works."""
    print_section("TEST 1: Symbol Normalization")
    assert normalize_symbol("  aapl ") == "AAPL"
    assert normalize_symbol("msft") == "MSFT"
    print("✅ normalize_symbol() works correctly")


def test_local_search() -> None:
    """Verify local search fallback works."""
    print_section("TEST 2b: Local Stock Search Fallback")
    results = search_stocks_local("Apple")
    print(f"Found {len(results)} local result(s) for 'Apple':")
    for item in results:
        print(f"  - {item['symbol']}: {item['name']}")
    assert any(item["symbol"] == "AAPL" for item in results)
    print("✅ search_stocks_local() works correctly")


def test_search_stocks() -> None:
    """Verify stock search returns results."""
    print_section("TEST 2: Stock Search")
    results = search_stocks("Apple")
    print(f"Found {len(results)} result(s) for 'Apple':")
    for item in results[:3]:
        print(f"  - {item['symbol']}: {item['name']} ({item['exchange']})")
    print("✅ search_stocks() works correctly")


def test_fetch_quote() -> None:
    """Verify quote fetching for a valid symbol."""
    print_section("TEST 3: Fetch Stock Quote (AAPL)")
    quote = fetch_stock_quote("AAPL", date_range="1mo")
    print(f"Symbol:        {quote['symbol']}")
    print(f"Current Price: {quote['current_price']}")
    print(f"Previous Close:{quote['previous_close']}")
    print(f"History Rows:  {len(quote['history'])}")
    print("✅ fetch_stock_quote() works correctly")


def test_fetch_history() -> None:
    """Verify historical data fetching."""
    print_section("TEST 4: Fetch Stock History (MSFT)")
    history = fetch_stock_history("MSFT", date_range="1mo")
    print(history.tail(3).to_string(index=False))
    print("✅ fetch_stock_history() works correctly")


def test_invalid_symbol() -> None:
    """Verify invalid symbols raise friendly errors."""
    print_section("TEST 5: Invalid Symbol Error Handling")
    try:
        fetch_stock_quote("INVALIDSYMBOL123")
        print("❌ Expected InvalidSymbolError but none was raised")
    except InvalidSymbolError as exc:
        print(f"✅ Caught expected error: {exc.message}")


def main() -> None:
    """Run all Module 2 verification tests."""
    print("Starting Module 2 tests for Stock Data Fetching...")

    tests = [
        test_symbol_normalization,
        test_local_search,
        test_search_stocks,
        test_fetch_quote,
        test_fetch_history,
        test_invalid_symbol,
    ]

    for test in tests:
        try:
            test()
        except Exception as exc:
            print(f"❌ {test.__name__} failed: {get_user_friendly_error(exc)}")
            raise

    print_section("ALL MODULE 2 TESTS PASSED ✅")


if __name__ == "__main__":
    main()
