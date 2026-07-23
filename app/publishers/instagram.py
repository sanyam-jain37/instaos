"""Instagram Graph API boundary without a live upload implementation."""

from datetime import UTC, datetime

from app.publishers.base import Publisher
from app.publishers.exceptions import AuthenticationError, PublisherValidationError
from app.publishers.models import HealthCheckResult, PublishRequest, PublishResult


class InstagramPublisher(Publisher):
    """Validates Instagram requests and isolates future Graph API integration."""

    provider_name = "instagram"

    def __init__(self, configured: bool = False) -> None:
        """Initializes the publisher without storing credentials."""
        self._configured = configured

    def validate(self, request: PublishRequest) -> None:
        """Validates fields required by a future Instagram upload."""
        if not request.account_name.strip():
            raise PublisherValidationError("Instagram account_name is required.")
        if not request.caption.strip():
            raise PublisherValidationError("Instagram caption must not be blank.")
        if not request.video_path:
            raise PublisherValidationError("Instagram video_path is required.")

    def publish(self, request: PublishRequest) -> PublishResult:
        """Rejects uploads until Graph API integration is implemented."""
        self.validate(request)
        if not self._configured:
            raise AuthenticationError("Instagram publisher is not configured.")
        raise NotImplementedError(
            "Instagram Graph API upload integration is not implemented."
        )

    def health_check(self) -> HealthCheckResult:
        """Reports whether configuration required for future API use is present."""
        return HealthCheckResult(
            healthy=self._configured,
            provider=self.provider_name,
            message=None if self._configured else "Instagram publisher is not configured.",
            checked_at=datetime.now(UTC),
        )

    def delete_post(self, post_id: str) -> bool:
        """Rejects deletion until Graph API integration is implemented."""
        if not self._configured:
            raise AuthenticationError("Instagram publisher is not configured.")
        raise NotImplementedError(
            "Instagram Graph API deletion integration is not implemented."
        )
