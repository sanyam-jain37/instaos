import pytest

from app.constants import AssetCategory
from app.database.models import File
from app.extractors.image_extractor import ImageExtractor
from app.extractors.models import ImageMetadata, VideoMetadata
from app.extractors.video_extractor import VideoExtractor


def build_file(category: AssetCategory) -> File:
    """Creates an indexed file model for extractor tests."""
    return File(
        drive_file_id="drive-file-1",
        name="asset",
        mime_type="application/octet-stream",
        category=category.value,
        full_path="My Drive/asset",
    )


def test_video_extractor_supports_video_assets() -> None:
    extractor = VideoExtractor()

    assert extractor.supports(build_file(AssetCategory.VIDEO)) is True
    assert extractor.supports(build_file(AssetCategory.IMAGE)) is False


def test_image_extractor_supports_image_assets() -> None:
    extractor = ImageExtractor()

    assert extractor.supports(build_file(AssetCategory.IMAGE)) is True
    assert extractor.supports(build_file(AssetCategory.VIDEO)) is False


def test_video_metadata_creation() -> None:
    metadata = VideoMetadata(
        duration_seconds=12.5,
        width=1920,
        height=1080,
        fps=30.0,
        codec="h264",
        bitrate=4_000_000,
        aspect_ratio=16 / 9,
    )

    assert metadata.width == 1920
    assert metadata.aspect_ratio == 16 / 9


def test_image_metadata_creation() -> None:
    metadata = ImageMetadata(
        width=1080,
        height=1350,
        format="JPEG",
        color_mode="RGB",
    )

    assert metadata.height == 1350
    assert metadata.color_mode == "RGB"


def test_video_extractor_extract_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError, match="FFmpeg integration"):
        VideoExtractor().extract(build_file(AssetCategory.VIDEO))


def test_image_extractor_extract_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError, match="Pillow integration"):
        ImageExtractor().extract(build_file(AssetCategory.IMAGE))
