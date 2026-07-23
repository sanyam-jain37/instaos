"""Reusable validation helpers for configuration models."""

from collections.abc import Iterable
from pathlib import Path
from typing import TypeVar

from pydantic import SecretStr


IdentifierT = TypeVar("IdentifierT")

MINIMUM_SECRET_LENGTH = 8
REDACTED_SECRET_VALUE = "********"


def validate_directory(path: Path) -> Path:
    """Validates that an existing path is a directory.

    Args:
        path: Configured directory path.

    Returns:
        The original directory path.

    Raises:
        ValueError: If the path exists but is not a directory.
    """
    if path.exists() and not path.is_dir():
        raise ValueError(f"Configured directory is a file: {path}")
    return path


def validate_secret_value(value: str | SecretStr | None) -> str | None:
    """Rejects blank and implausibly short configured secrets.

    Args:
        value: Raw secret value before conversion to a secret type.

    Returns:
        The validated secret value.

    Raises:
        ValueError: If the value is blank or too short.
    """
    if value is None:
        return None

    if isinstance(value, SecretStr):
        value = value.get_secret_value()

    if (
        not value.strip()
        or len(value) < MINIMUM_SECRET_LENGTH
        or value == REDACTED_SECRET_VALUE
    ):
        raise ValueError("Secret values must contain at least eight characters.")
    return value


def ensure_unique(values: Iterable[IdentifierT], label: str) -> None:
    """Validates that identifiers are unique after normalization.

    Args:
        values: Identifier values to check.
        label: Human-readable label for the identifiers.

    Raises:
        ValueError: If duplicate identifiers are present.
    """
    normalized = [str(value).casefold() for value in values]
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"Duplicate {label} values are not allowed.")
