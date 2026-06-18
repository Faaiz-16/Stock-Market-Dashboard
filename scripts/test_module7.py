"""
Module 7 test script — Final Integration

Runs end-to-end tests across all modules:

    fetch → process → analytics → charts

Run from the project root:

    python scripts/test_module7.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DEFAULT_STOCKS  # noqa: E402
from src.analytics import calculate_analytics  # noqa: E402
from src.data_fetcher import fetch_stock_quote  # noqa: E402
from src.data_processor import process_stock_data  # noqa: E402
from src.pipeline import load_dashboard_data  # noqa: E402
from src.ui.charts import (  # noqa: E402
    create_candlestick_chart,
    create_daily_returns_chart,
    create_line_chart,
    create_moving_average_chart,
    create_volume_chart,
)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_pipeline_end_to_end() -> None:
    """Verify the unified pipeline produces complete dashboard data."""
    print_section("TEST 1: Unified Pipeline (AAPL)")
    data = load_dashboard_data("AAPL", "1mo")

    assert "processed" in data, "Missing processed data"
    assert "analytics" in data, "Missing analytics data"

    processed = data["processed"]
    analytics = data["analytics"]

    print(f"  Symbol:       {processed['symbol']}")
    print(f"  Data Source:  {processed['data_source']}")
    print(f"  History Rows: {len(processed['history'])}")
    print(f"  Current Price:${processed['indicators']['current_price']}")
    print(f"  Highest:      ${analytics['highest_price']}")
    print(f"  Volatility:   {analytics['volatility']}%")
    print("✅ load_dashboard_data() pipeline works end-to-end")


def test_all_default_stocks() -> None:
    """Verify pipeline works for every default stock symbol."""
    print_section("TEST 2: All Default Stocks")
    for symbol in DEFAULT_STOCKS:
        data = load_dashboard_data(symbol, "1mo")
        price = data["processed"]["indicators"]["current_price"]
        source = data["processed"]["data_source"]
        print(f"  ✅ {symbol}: ${price} via {source}")
    print("✅ All default stocks load successfully")


def test_module_chain() -> None:
    """Verify each module output feeds correctly into the next."""
    print_section("TEST 3: Module Chain (MSFT)")

    # Module 2: Fetch
    quote = fetch_stock_quote("MSFT", "3mo")
    assert "history" in quote
    print("  ✅ Module 2 — data_fetcher")

    # Module 3: Process
    processed = process_stock_data(quote)
    assert "indicators" in processed
    assert "MA_7" in processed["history"].columns
    print("  ✅ Module 3 — data_processor")

    # Module 6: Analytics
    analytics = calculate_analytics(processed["history"])
    assert analytics["highest_price"] >= analytics["lowest_price"]
    print("  ✅ Module 6 — analytics")

    # Module 5: Charts (verify figures build from processed data)
    history = processed["history"]
    charts = [
        ("Line", create_line_chart(history, "MSFT")),
        ("Candlestick", create_candlestick_chart(history, "MSFT")),
        ("Volume", create_volume_chart(history, "MSFT")),
        ("Returns", create_daily_returns_chart(history, "MSFT")),
        ("MA", create_moving_average_chart(history, "MSFT")),
    ]
    for name, fig in charts:
        assert len(fig.data) > 0, f"{name} chart has no traces"
    print("  ✅ Module 5 — charts build from processed data")

    print("✅ Full module chain connected correctly")


def test_googl_nvda_integration() -> None:
    """Verify previously problematic stocks work through the pipeline."""
    print_section("TEST 4: GOOGL & NVDA Integration")
    for symbol in ["GOOGL", "NVDA"]:
        data = load_dashboard_data(symbol, "1mo")
        price = data["processed"]["indicators"]["current_price"]
        print(f"  ✅ {symbol}: ${price} via {data['processed']['data_source']}")
    print("✅ GOOGL and NVDA integrated successfully")


def test_ui_module_imports() -> None:
    """Verify all UI modules import for the integrated dashboard."""
    print_section("TEST 5: UI Module Imports")
    from src.ui import (  # noqa: F401
        analytics_cards,
        chart_renderer,
        charts,
        header,
        layout,
        sidebar,
        stats_cards,
        styles,
    )

    modules = [
        "layout", "sidebar", "header", "stats_cards",
        "charts", "chart_renderer", "analytics_cards",
        "styles",
    ]
    for name in modules:
        print(f"  ✅ ui.{name}")
    print("✅ All UI modules import successfully")


def test_app_entry_point() -> None:
    """Verify the main app entry point imports without errors."""
    print_section("TEST 6: App Entry Point")
    import app  # noqa: F401

    assert hasattr(app, "main"), "app.py missing main()"
    assert hasattr(app, "configure_page"), "app.py missing configure_page()"
    print("  ✅ app.py imports successfully")
    print("  ✅ main() and configure_page() defined")
    print("✅ App entry point is ready")


def main() -> None:
    """Run all Module 7 integration tests."""
    print("Starting Module 7 tests for Final Integration...")

    tests = [
        test_pipeline_end_to_end,
        test_all_default_stocks,
        test_module_chain,
        test_googl_nvda_integration,
        test_ui_module_imports,
        test_app_entry_point,
    ]

    for test in tests:
        test()

    print_section("ALL MODULE 7 TESTS PASSED ✅")
    print("\n🎉 Dashboard is fully integrated and ready to run:")
    print("   streamlit run app.py")


if __name__ == "__main__":
    main()
