"""Image metadata extractor interface implementation."""

from app.constants import AssetCategory
from app.database.models import File
from app.extractors.base import MediaExtractor
from app.extractors.models import ImageMetadata


class ImageExtractor(MediaExtractor[ImageMetadata]):
    """Identifies image assets for future Pillow-based extraction."""

    def supports(self, file: File) -> bool:
        """Reports whether an asset is categorized as an image.

        Args:
            file: Indexed asset to evaluate.

        Returns:
            ``True`` when the asset has the image category; otherwise ``False``.
        """
        return file.category == AssetCategory.IMAGE.value

    def extract(self, file: File) -> ImageMetadata:
        """Raises until Pillow-backed extraction is implemented.

        Args:
            file: Indexed image asset to inspect.

        Raises:
            NotImplementedError: Pillow integration is scheduled for a future
                sprint.
        """
        raise NotImplementedError(
            "Pillow integration for image metadata extraction will be added "
            "in a future sprint."
        )
