"""Exceptions raised by the InstaOS configuration system."""

from collections.abc import Sequence


class ConfigurationError(Exception):
    """Base exception for configuration loading and validation failures."""


class MissingConfiguration(ConfigurationError):
    """Raised when an explicitly requested configuration source is absent."""


class InvalidConfiguration(ConfigurationError):
    """Raised when configuration content cannot be parsed or is unsafe."""


class ValidationError(InvalidConfiguration):
    """Raised when configuration values do not satisfy the schema.

    Args:
        messages: Sanitized validation messages that never include secret values.
    """

    def __init__(self, messages: Sequence[str]) -> None:
        self.messages = tuple(messages)
        super().__init__("; ".join(self.messages))
