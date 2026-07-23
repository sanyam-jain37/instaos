"""Interfaces and data models for media metadata extraction."""

from app.extractors.image_extractor import ImageExtractor
from app.extractors.models import ImageMetadata, VideoMetadata
from app.extractors.video_extractor import VideoExtractor

__all__ = [
    "ImageExtractor",
    "ImageMetadata",
    "VideoExtractor",
    "VideoMetadata",
]
