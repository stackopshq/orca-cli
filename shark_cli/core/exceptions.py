"""Custom exceptions for shark-cli."""

import click


class SharkCLIError(click.ClickException):
    """Base exception for all shark-cli errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class AuthenticationError(SharkCLIError):
    """Raised when API authentication fails (HTTP 401/403)."""

    def __init__(self, message: str = "Authentication failed. Run 'shark setup' to configure your API key.") -> None:
        super().__init__(message)


class APIError(SharkCLIError):
    """Raised when the Sharktech API returns an unexpected error."""

    def __init__(self, status_code: int, detail: str = "") -> None:
        msg = f"API error (HTTP {status_code})"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class ConfigurationError(SharkCLIError):
    """Raised when the CLI configuration is missing or invalid."""

    def __init__(self, message: str = "Configuration not found. Run 'shark setup' first.") -> None:
        super().__init__(message)
