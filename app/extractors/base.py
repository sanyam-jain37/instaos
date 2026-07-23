"""Base contract for media metadata extractors."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.database.models import File


MetadataT = TypeVar("MetadataT")


class MediaExtractor(ABC, Generic[MetadataT]):
    """Defines the interface for media-specific metadata extractors."""

    @abstractmethod
    def supports(self, file: File) -> bool:
        """Reports whether this extractor can process an indexed asset.

        Args:
            file: Indexed asset to evaluate.

        Returns:
            ``True`` when the extractor supports the asset; otherwise ``False``.
        """

    @abstractmethod
    def extract(self, file: File) -> MetadataT:
        """Extracts structured metadata from an indexed asset.

        Args:
            file: Indexed asset to inspect.

        Returns:
            Media-specific metadata for the provided asset.
        """
