"""Abstract contract for social publishing providers."""

from abc import ABC, abstractmethod

from app.publishers.models import HealthCheckResult, PublishRequest, PublishResult


class Publisher(ABC):
    """Provider-independent publishing interface."""

    @abstractmethod
    def validate(self, request: PublishRequest) -> None:
        """Validates a publish request before provider execution."""

    @abstractmethod
    def publish(self, request: PublishRequest) -> PublishResult:
        """Publishes one request and returns its provider outcome."""

    @abstractmethod
    def health_check(self) -> HealthCheckResult:
        """Returns the current provider health state."""

    @abstractmethod
    def delete_post(self, post_id: str) -> bool:
        """Deletes a provider post when supported."""
