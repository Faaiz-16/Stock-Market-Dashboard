"""
Custom exceptions for the Stock Market Dashboard.

Each exception maps to a specific failure scenario so the app can
show clear, user-friendly error messages.
"""


class StockDashboardError(Exception):
    """Base exception for all dashboard-related errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidSymbolError(StockDashboardError):
    """Raised when a stock symbol is invalid or not found."""


class ConnectionError(StockDashboardError):
    """Raised when the app cannot reach the internet or API server."""


class APIError(StockDashboardError):
    """Raised when the API returns an unexpected or failed response."""


class EmptyDataError(StockDashboardError):
    """Raised when the API returns no usable stock data."""


class RateLimitError(StockDashboardError):
    """Raised when the API rate limit is exceeded (HTTP 429)."""
