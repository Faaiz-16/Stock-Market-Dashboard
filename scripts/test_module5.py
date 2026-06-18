"""
Module 5 test script — Plotly Visualizations

Run from the project root:

    python scripts/test_module5.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import plotly.graph_objects as go  # noqa: E402

from src.data_fetcher import fetch_stock_quote  # noqa: E402
from src.data_processor import process_stock_data  # noqa: E402
from src.ui.charts import (  # noqa: E402
    create_candlestick_chart,
    create_combined_price_volume_chart,
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


def _assert_figure(name: str, figure: go.Figure) -> None:
    """Verify a Plotly figure was created with data traces."""
    assert isinstance(figure, go.Figure), f"{name}: not a Plotly Figure"
    assert len(figure.data) > 0, f"{name}: no data traces"
    print(f"  ✅ {name} — {len(figure.data)} trace(s), height={figure.layout.height}")


def test_line_chart() -> None:
    """Verify line chart creation."""
    print_section("TEST 1: Line Chart")
    processed = process_stock_data(fetch_stock_quote("AAPL", "1mo"))
    figure = create_line_chart(processed["history"], "AAPL")
    _assert_figure("Line Chart", figure)


def test_candlestick_chart() -> None:
    """Verify candlestick chart creation."""
    print_section("TEST 2: Candlestick Chart")
    processed = process_stock_data(fetch_stock_quote("MSFT", "1mo"))
    figure = create_candlestick_chart(processed["history"], "MSFT")
    _assert_figure("Candlestick Chart", figure)


def test_volume_chart() -> None:
    """Verify volume chart creation."""
    print_section("TEST 3: Volume Chart")
    processed = process_stock_data(fetch_stock_quote("TSLA", "1mo"))
    figure = create_volume_chart(processed["history"], "TSLA")
    _assert_figure("Volume Chart", figure)


def test_daily_returns_chart() -> None:
    """Verify daily returns chart creation."""
    print_section("TEST 4: Daily Returns Chart")
    processed = process_stock_data(fetch_stock_quote("AMZN", "1mo"))
    figure = create_daily_returns_chart(processed["history"], "AMZN")
    _assert_figure("Daily Returns Chart", figure)


def test_moving_average_chart() -> None:
    """Verify moving average chart creation."""
    print_section("TEST 5: Moving Average Chart")
    processed = process_stock_data(fetch_stock_quote("GOOGL", "1mo"))
    figure = create_moving_average_chart(processed["history"], "GOOGL")
    _assert_figure("Moving Average Chart", figure)
    assert len(figure.data) == 3, "MA chart should have 3 traces (Close, MA_7, MA_30)"


def test_combined_overview_chart() -> None:
    """Verify combined price + volume chart creation."""
    print_section("TEST 6: Combined Overview Chart")
    processed = process_stock_data(fetch_stock_quote("NVDA", "1mo"))
    figure = create_combined_price_volume_chart(processed["history"], "NVDA")
    _assert_figure("Combined Overview Chart", figure)
    assert len(figure.data) == 2, "Overview chart should have 2 traces (candlestick + volume)"


def test_chart_interactivity() -> None:
    """Verify charts have hover/interaction settings enabled."""
    print_section("TEST 7: Chart Interactivity Settings")
    processed = process_stock_data(fetch_stock_quote("AAPL", "1mo"))
    figure = create_line_chart(processed["history"], "AAPL")

    assert figure.layout.hovermode == "x unified", "Hover mode should be 'x unified'"
    assert figure.data[0].hovertemplate is not None, "Hover template should be set"
    print("  ✅ Hover mode: x unified")
    print("  ✅ Hover templates: configured")
    print("✅ Charts are interactive-ready")


def main() -> None:
    """Run all Module 5 verification tests."""
    print("Starting Module 5 tests for Plotly Visualizations...")

    tests = [
        test_line_chart,
        test_candlestick_chart,
        test_volume_chart,
        test_daily_returns_chart,
        test_moving_average_chart,
        test_combined_overview_chart,
        test_chart_interactivity,
    ]

    for test in tests:
        test()

    print_section("ALL MODULE 5 TESTS PASSED ✅")


if __name__ == "__main__":
    main()
