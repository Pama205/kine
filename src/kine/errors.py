# kine/errors.py
class KineError(Exception):
    """Base class for all library errors."""

    pass


class ProviderAPIError(KineError):
    """Raised when a provider API call fails."""

    pass


class ProviderNotFoundError(KineError):
    """Raised when a provider is not registered."""

    pass


class APIKeyNotFoundError(KineError):
    """Raised when an API key is missing."""

    pass


class APIModelNotFoundError(KineError):
    """Raised when an API model is missing."""

    pass
