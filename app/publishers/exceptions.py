"""Typed errors for publishing providers."""


class PublisherError(Exception):
    """Base error raised by publishing providers."""

    retryable = False


class PublisherValidationError(PublisherError):
    """Raised when a publish request is invalid."""


class UploadError(PublisherError):
    """Raised when a provider cannot upload supplied media."""


class AuthenticationError(PublisherError):
    """Raised when provider authentication is invalid or unavailable."""


class RateLimitError(PublisherError):
    """Raised when a provider rate limit requires a retry."""

    retryable = True


class TemporaryPublisherError(PublisherError):
    """Raised for transient provider failures that may be retried."""

    retryable = True


class PermanentPublisherError(PublisherError):
    """Raised for provider failures that must not be retried."""
