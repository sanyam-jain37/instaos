from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.publishers.exceptions import PermanentPublisherError, TemporaryPublisherError
from app.publishers.factory import PublisherFactory
from app.publishers.instagram import InstagramPublisher
from app.publishers.mock import MockPublisher
from app.publishers.models import PublishRequest
from app.publishers.retry import RetryPolicy


def request() -> PublishRequest:
    """Builds a valid deterministic test request."""
    return PublishRequest(
        video_path=Path("video.mp4"),
        caption="A caption",
        account_name="account",
        scheduled_time=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_mock_publisher_publishes_and_deletes_deterministically() -> None:
    publisher = MockPublisher(clock=lambda: datetime(2026, 1, 1, tzinfo=UTC))

    result = publisher.publish(request())

    assert result.post_id == "mock-00000001"
    assert publisher.delete_post(result.post_id or "") is True
    assert publisher.delete_post(result.post_id or "") is False


def test_mock_publisher_simulates_retryable_and_permanent_failures() -> None:
    with pytest.raises(TemporaryPublisherError):
        MockPublisher(failure_count=1).publish(request())
    with pytest.raises(PermanentPublisherError):
        MockPublisher(failure_count=1, retryable_failures=False).publish(request())


def test_retry_policy_retries_only_transient_errors() -> None:
    attempts = 0
    delays: list[float] = []

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise TemporaryPublisherError("retry")
        return "ok"

    assert RetryPolicy(3, 1.0, 2.0, delays.append).execute(operation) == "ok"
    assert delays == [1.0, 2.0]


def test_factory_and_instagram_skeleton_behaviour() -> None:
    factory = PublisherFactory()
    assert isinstance(factory.create("mock"), MockPublisher)
    publisher = factory.create("instagram")
    assert isinstance(publisher, InstagramPublisher)
    assert publisher.health_check().healthy is False
    with pytest.raises(Exception):
        publisher.publish(request())
