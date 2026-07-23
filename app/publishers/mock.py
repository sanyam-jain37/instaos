"""Deterministic in-memory publisher for tests and local development."""

from collections.abc import Callable
from datetime import UTC, datetime
from time import sleep

from app.publishers.base import Publisher
from app.publishers.exceptions import PermanentPublisherError, TemporaryPublisherError
from app.publishers.models import HealthCheckResult, PublishRequest, PublishResult


class MockPublisher(Publisher):
    """Deterministic provider that simulates bounded configured failures."""

    provider_name = "mock"

    def __init__(
        self,
        failure_count: int = 0,
        retryable_failures: bool = True,
        delay_seconds: float = 0.0,
        sleeper: Callable[[float], None] = sleep,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        healthy: bool = True,
    ) -> None:
        """Initializes deterministic simulation controls.

        Args:
            failure_count: Number of initial publishes that fail.
            retryable_failures: Whether configured failures are transient.
            delay_seconds: Simulated delay for each publish call.
            sleeper: Injectable delay implementation.
            clock: Injectable UTC clock.
            healthy: Simulated provider health.
        """
        if failure_count < 0 or delay_seconds < 0:
            raise ValueError("failure_count and delay_seconds must be non-negative.")
        self._remaining_failures = failure_count
        self._retryable_failures = retryable_failures
        self._delay_seconds = delay_seconds
        self._sleeper = sleeper
        self._clock = clock
        self._healthy = healthy
        self._next_post_number = 1
        self._posts: set[str] = set()

    def validate(self, request: PublishRequest) -> None:
        """Validates local mock publishing requirements."""
        if not request.video_path:
            raise ValueError("video_path is required.")
        if not request.caption.strip():
            raise ValueError("caption must not be blank.")

    def publish(self, request: PublishRequest) -> PublishResult:
        """Simulates a deterministic publish attempt."""
        self.validate(request)
        if self._delay_seconds:
            self._sleeper(self._delay_seconds)
        if self._remaining_failures:
            self._remaining_failures -= 1
            if self._retryable_failures:
                raise TemporaryPublisherError("Configured transient mock failure.")
            raise PermanentPublisherError("Configured permanent mock failure.")

        post_id = f"mock-{self._next_post_number:08d}"
        self._next_post_number += 1
        self._posts.add(post_id)
        return PublishResult(
            success=True,
            provider=self.provider_name,
            post_id=post_id,
            published_at=self._clock(),
            duration_seconds=self._delay_seconds,
        )

    def health_check(self) -> HealthCheckResult:
        """Returns deterministic simulated health."""
        return HealthCheckResult(
            healthy=self._healthy,
            provider=self.provider_name,
            message=None if self._healthy else "Mock publisher is unhealthy.",
            checked_at=self._clock(),
        )

    def delete_post(self, post_id: str) -> bool:
        """Deletes a simulated post if it exists."""
        if post_id not in self._posts:
            return False
        self._posts.remove(post_id)
        return True
