"""
Main dashboard layout component.

Module 7: Fully integrated dashboard connecting all modules:
    - Sidebar controls      (Module 4)
    - Data pipeline         (Modules 2 + 3 + 6)
    - Statistics cards      (Module 4)
    - Plotly charts         (Module 5)
    - Analytics section     (Module 6)
"""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from src.data_fetcher import get_user_friendly_error
from src.pipeline import DashboardData, load_dashboard_data
from src.ui.analytics_cards import render_analytics_section
from src.ui.chart_renderer import render_charts
from src.ui.header import render_header
from src.ui.sidebar import (
    SESSION_LAST_UPDATED,
    SidebarFilters,
    clear_refresh_flag,
    render_sidebar,
    set_last_updated,
)
from src.ui.stats_cards import render_statistics_cards, render_stock_summary
from src.ui.styles import apply_custom_styles

# Session keys for cached dashboard state
SESSION_DASHBOARD_DATA: str = "dashboard_data"


def _needs_data_reload(filters: SidebarFilters) -> bool:
    """
    Determine whether fresh data must be fetched.

    Reloads when:
        - Refresh flag is set (user clicked Refresh or changed filters)
        - No cached data exists yet
        - Cached symbol or date range differs from current sidebar selection
    """
    if filters.refresh:
        return True

    if SESSION_DASHBOARD_DATA not in st.session_state:
        return True

    cached: DashboardData = st.session_state[SESSION_DASHBOARD_DATA]
    processed = cached["processed"]

    if processed["symbol"] != filters.symbol:
        return True

    if processed["date_range"] != filters.date_range:
        return True

    return False


def _load_dashboard_data(filters: SidebarFilters) -> DashboardData | None:
    """
    Fetch, process, and analyse stock data through the integrated pipeline.

    Args:
        filters: Current sidebar filter selections

    Returns:
        DashboardData on success, None on failure
    """
    with st.spinner(f"Loading dashboard for {filters.symbol}..."):
        try:
            data = load_dashboard_data(
                symbol=filters.symbol,
                date_range=filters.date_range,
            )

            # Cache the integrated result
            st.session_state[SESSION_DASHBOARD_DATA] = data
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            set_last_updated(timestamp)

            return data

        except Exception as exc:
            st.error(get_user_friendly_error(exc))
            return None
        finally:
            clear_refresh_flag()


def _render_data_table(data: DashboardData) -> None:
    """Show the full processed dataset in a collapsible table."""
    with st.expander("View Raw Data", expanded=False):
        display_columns = [
            "Date", "Open", "High", "Low", "Close",
            "Volume", "MA_7", "MA_30", "Daily_Return",
        ]
        st.dataframe(
            data["processed"]["history"][display_columns],
            use_container_width=True,
            hide_index=True,
        )


def render_dashboard() -> None:
    """
    Render the fully integrated Stock Market Dashboard.

    Complete layout:
        1. Custom CSS
        2. Sidebar filters
        3. Integrated data pipeline (fetch → process → analyse)
        4. Header
        5. Stock summary bar
        6. Statistics cards
        7. Interactive Plotly charts
        8. Analytics section
        9. Raw data table
    """
    # --- Module 4: Sidebar controls ---
    filters = render_sidebar()

    apply_custom_styles()

    # --- Modules 2+3+6: Integrated data pipeline ---
    if _needs_data_reload(filters):
        data = _load_dashboard_data(filters)
    else:
        data = st.session_state[SESSION_DASHBOARD_DATA]

    # --- Header ---
    active_symbol = filters.symbol if data is None else data["processed"]["symbol"]
    render_header(symbol=active_symbol)

    if data is None:
        st.info("Select a stock and click **Refresh Data** to load the dashboard.")
        return

    processed = data["processed"]

    # --- Stock summary ---
    render_stock_summary(
        symbol=processed["symbol"],
        data_source=processed["data_source"],
        date_range=processed["date_range"],
    )

    st.divider()

    # --- Module 4: Statistics cards ---
    render_statistics_cards(processed["indicators"])

    st.divider()

    # --- Module 5: Interactive Plotly charts ---
    render_charts(processed)

    st.divider()

    # --- Module 6: Analytics section ---
    render_analytics_section(processed)

    # --- Raw data table ---
    _render_data_table(data)
