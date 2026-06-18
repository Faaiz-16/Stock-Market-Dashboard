"""
Formatting helpers for displaying prices, volumes, and percentages.
"""


def format_price(value: float | None) -> str:
    """Format a price value as a USD currency string."""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def format_volume(value: int | float | None) -> str:
    """Format trading volume with thousands separators."""
    if value is None:
        return "N/A"
    return f"{int(value):,}"


def format_change_percent(value: float | None) -> str:
    """Format a percentage change with +/- sign."""
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def get_change_delta(value: float | None) -> str | None:
    """
    Return a delta string for Streamlit metric components.

    Streamlit metrics show green/red based on delta value.
    """
    if value is None:
        return None
    return f"{value:.2f}%"
