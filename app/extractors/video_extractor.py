"""Video metadata extractor interface implementation."""

from app.constants import AssetCategory
from app.database.models import File
from app.extractors.base import MediaExtractor
from app.extractors.models import VideoMetadata


class VideoExtractor(MediaExtractor[VideoMetadata]):
    """Identifies video assets for future FFmpeg-based extraction."""

    def supports(self, file: File) -> bool:
        """Reports whether an asset is categorized as a video.

        Args:
            file: Indexed asset to evaluate.

        Returns:
            ``True`` when the asset has the video category; otherwise ``False``.
        """
        return file.category == AssetCategory.VIDEO.value

    def extract(self, file: File) -> VideoMetadata:
        """Raises until FFmpeg-backed extraction is implemented.

        Args:
            file: Indexed video asset to inspect.

        Raises:
            NotImplementedError: FFmpeg integration is scheduled for a future
                sprint.
        """
        raise NotImplementedError(
            "FFmpeg integration for video metadata extraction will be added "
            "in the next sprint."
        )
