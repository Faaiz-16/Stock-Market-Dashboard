"""
Sidebar controls for the dashboard.

Provides stock selection, search, date range filter, and refresh button.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import streamlit as st

from config.settings import (
    DATE_RANGE_LABELS,
    DEFAULT_DATE_RANGE,
    DEFAULT_STOCKS,
    KNOWN_STOCKS,
    VALID_DATE_RANGES,
)
from src.data_fetcher import get_user_friendly_error, normalize_symbol, search_stocks

# Session state keys — centralized to avoid typos
SESSION_SYMBOL: Final[str] = "selected_symbol"
SESSION_DATE_RANGE: Final[str] = "date_range"
SESSION_REFRESH: Final[str] = "refresh_requested"
SESSION_LAST_UPDATED: Final[str] = "last_updated"
PENDING_SYMBOL: Final[str] = "pending_symbol"
PENDING_MESSAGE: Final[str] = "pending_message"


@dataclass
class SidebarFilters:
    """User-selected filter values from the sidebar."""

    symbol: str
    date_range: str
    refresh: bool


def _init_sidebar_state() -> None:
    """Set default session state values on first app load."""
    if SESSION_SYMBOL not in st.session_state:
        st.session_state[SESSION_SYMBOL] = DEFAULT_STOCKS[0]

    if SESSION_DATE_RANGE not in st.session_state:
        st.session_state[SESSION_DATE_RANGE] = DEFAULT_DATE_RANGE

    if SESSION_REFRESH not in st.session_state:
        st.session_state[SESSION_REFRESH] = True  # Load data on first visit


def _apply_pending_symbol() -> None:
    """
    Apply a pending symbol change BEFORE the selectbox widget is created.

    Streamlit does not allow modifying a widget's session-state key after
    that widget has been rendered in the same run. Quick Pick and Search
    store the desired symbol in PENDING_SYMBOL, then rerun. This function
    applies it at the top of the next run, before any widgets exist.
    """
    if PENDING_SYMBOL not in st.session_state:
        return

    st.session_state[SESSION_SYMBOL] = st.session_state.pop(PENDING_SYMBOL)
    st.session_state[SESSION_REFRESH] = True


def _request_symbol_change(symbol: str, message: str | None = None) -> None:
    """
    Queue a stock symbol change and rerun the app.

    Args:
        symbol: Stock ticker to switch to
        message: Optional sidebar success message shown after rerun
    """
    st.session_state[PENDING_SYMBOL] = normalize_symbol(symbol)
    st.session_state[SESSION_REFRESH] = True
    if message:
        st.session_state[PENDING_MESSAGE] = message
    st.rerun()


def _show_pending_message() -> None:
    """Display a one-time message queued by search or quick pick."""
    if PENDING_MESSAGE in st.session_state:
        st.sidebar.success(st.session_state.pop(PENDING_MESSAGE))


def _on_symbol_change() -> None:
    """Trigger a data refresh when the user changes the stock dropdown."""
    st.session_state[SESSION_REFRESH] = True


def _on_date_range_change() -> None:
    """Trigger a data refresh when the user changes the date range."""
    st.session_state[SESSION_REFRESH] = True


def _apply_search_result(search_query: str) -> None:
    """Run symbol search and queue the top result as the new selected stock."""
    try:
        results = search_stocks(search_query)
        if results:
            match = results[0]
            message = f"Selected: {match['symbol']} — {match['name']}"
            _request_symbol_change(match["symbol"], message=message)
    except Exception as exc:
        st.sidebar.error(get_user_friendly_error(exc))


def render_sidebar() -> SidebarFilters:
    """
    Render all sidebar controls and return the current filter selections.

    Sidebar includes:
        - Stock dropdown
        - Symbol search box
        - Date range selector
        - Refresh button
        - Quick-pick popular stocks

    Returns:
        SidebarFilters with symbol, date_range, and refresh flag
    """
    _init_sidebar_state()
    _apply_pending_symbol()

    with st.sidebar:
        st.header("📊 Dashboard Controls")
        _show_pending_message()
        st.markdown("---")

        # --- Stock selection dropdown ---
        st.subheader("Select Stock")

        # Include searched symbol in dropdown even if not in default list
        dropdown_options = list(DEFAULT_STOCKS)
        current_symbol = st.session_state[SESSION_SYMBOL]
        if current_symbol not in dropdown_options:
            dropdown_options = [current_symbol] + dropdown_options

        selected = st.selectbox(
            label="Stock Symbol",
            options=dropdown_options,
            key=SESSION_SYMBOL,
            on_change=_on_symbol_change,
            label_visibility="collapsed",
        )

        # Show company name below the dropdown
        company_name = KNOWN_STOCKS.get(selected, "Unknown Company")
        st.caption(f"**{selected}** — {company_name}")

        st.markdown("---")

        # --- Search box ---
        st.subheader("Search Stocks")
        search_query = st.text_input(
            label="Search",
            placeholder="e.g., Apple, NVDA, Tesla",
            key="sidebar_search",
            label_visibility="collapsed",
        )

        if st.button("🔍 Search", use_container_width=True, key="sidebar_search_btn"):
            if search_query.strip():
                _apply_search_result(search_query)
            else:
                st.sidebar.warning("Enter a symbol or company name to search.")

        st.markdown("---")

        # --- Date range selector ---
        st.subheader("Date Range")
        date_range = st.selectbox(
            label="Date Range",
            options=VALID_DATE_RANGES,
            format_func=lambda value: DATE_RANGE_LABELS.get(value, value),
            key=SESSION_DATE_RANGE,
            on_change=_on_date_range_change,
            label_visibility="collapsed",
        )

        st.markdown("---")

        # --- Refresh button ---
        refresh_clicked = st.button(
            "🔄 Refresh Data",
            use_container_width=True,
            type="primary",
            key="sidebar_refresh_btn",
        )

        if refresh_clicked:
            st.session_state[SESSION_REFRESH] = True

        # Show last updated timestamp if available
        if SESSION_LAST_UPDATED in st.session_state:
            st.caption(f"Last updated: {st.session_state[SESSION_LAST_UPDATED]}")

        st.markdown("---")

        # --- Quick-pick buttons for popular stocks ---
        st.subheader("Quick Pick")
        quick_cols = st.columns(3)
        for index, symbol in enumerate(DEFAULT_STOCKS[:6]):
            col = quick_cols[index % 3]
            if col.button(symbol, key=f"quick_{symbol}", use_container_width=True):
                _request_symbol_change(symbol)

    return SidebarFilters(
        symbol=normalize_symbol(st.session_state[SESSION_SYMBOL]),
        date_range=st.session_state[SESSION_DATE_RANGE],
        refresh=st.session_state[SESSION_REFRESH],
    )


def clear_refresh_flag() -> None:
    """Reset the refresh flag after data has been loaded."""
    st.session_state[SESSION_REFRESH] = False


def set_last_updated(timestamp: str) -> None:
    """Store the last successful data fetch timestamp in session state."""
    st.session_state[SESSION_LAST_UPDATED] = timestamp
