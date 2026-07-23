"""Immutable data contracts for publishing providers."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Mapping


def _immutable_metadata(metadata: Mapping[str, object]) -> Mapping[str, object]:
    """Copies metadata into an immutable mapping."""
    return MappingProxyType(dict(metadata))


@dataclass(frozen=True, slots=True)
class PublishRequest:
    """A validated request to publish one media asset."""

    video_path: Path
    caption: str
    account_name: str
    asset_id: int | None = None
    hashtags: tuple[str, ...] = ()
    thumbnail_path: Path | None = None
    scheduled_time: datetime | None = None
    account_id: int | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validates timestamp awareness and freezes metadata."""
        if not self.account_name.strip():
            raise ValueError("account_name must not be blank.")
        if self.scheduled_time and self.scheduled_time.tzinfo is None:
            raise ValueError("scheduled_time must be timezone-aware.")
        object.__setattr__(self, "metadata", _immutable_metadata(self.metadata))


@dataclass(frozen=True, slots=True)
class PublishResult:
    """Outcome of one provider publish attempt."""

    success: bool
    provider: str
    duration_seconds: float
    post_id: str | None = None
    published_at: datetime | None = None
    error_message: str | None = None
    retryable: bool = False
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validates aware timestamps and freezes metadata."""
        if self.published_at and self.published_at.tzinfo is None:
            raise ValueError("published_at must be timezone-aware.")
        object.__setattr__(self, "metadata", _immutable_metadata(self.metadata))


@dataclass(frozen=True, slots=True)
class HealthCheckResult:
    """Provider health state at a specific UTC instant."""

    healthy: bool
    provider: str
    checked_at: datetime
    message: str | None = None

    def __post_init__(self) -> None:
        """Requires an aware check timestamp."""
        if self.checked_at.tzinfo is None:
            raise ValueError("checked_at must be timezone-aware.")
