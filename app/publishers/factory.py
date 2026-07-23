"""Factory for constructing supported publishing providers."""

from app.publishers.base import Publisher
from app.publishers.exceptions import PublisherValidationError
from app.publishers.instagram import InstagramPublisher
from app.publishers.mock import MockPublisher


class PublisherFactory:
    """Constructs provider implementations from supported provider names."""

    MOCK = "mock"
    INSTAGRAM = "instagram"

    def create(self, provider_name: str, configured: bool = False) -> Publisher:
        """Creates a supported publishing provider.

        Args:
            provider_name: Case-insensitive provider identifier.
            configured: Whether provider credentials are available externally.

        Returns:
            A publisher implementation.

        Raises:
            PublisherValidationError: If the provider is unsupported.
        """
        normalized_name = provider_name.casefold()
        if normalized_name == self.MOCK:
            return MockPublisher()
        if normalized_name == self.INSTAGRAM:
            return InstagramPublisher(configured=configured)
        raise PublisherValidationError(f"Unsupported publisher: {provider_name}")
