"""Structured metadata returned by media extractors."""

from dataclasses import dataclass


@dataclass(frozen=True)
class VideoMetadata:
    """Technical metadata extracted from a video asset.

    Attributes:
        duration_seconds: Video duration in seconds.
        width: Frame width in pixels.
        height: Frame height in pixels.
        fps: Frames per second.
        codec: Video codec name.
        bitrate: Video bitrate in bits per second.
        aspect_ratio: Frame width divided by frame height.
    """

    duration_seconds: float
    width: int
    height: int
    fps: float
    codec: str
    bitrate: int
    aspect_ratio: float


@dataclass(frozen=True)
class ImageMetadata:
    """Technical metadata extracted from an image asset.

    Attributes:
        width: Image width in pixels.
        height: Image height in pixels.
        format: Image container format, such as ``JPEG`` or ``PNG``.
        color_mode: Image color mode, such as ``RGB`` or ``RGBA``.
    """

    width: int
    height: int
    format: str
    color_mode: str
