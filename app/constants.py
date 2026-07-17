"""Shared constants for InstaOS domain concepts."""

from enum import Enum


class AssetCategory(str, Enum):
    """Categories assigned to assets during metadata extraction."""

    VIDEO = "VIDEO"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    PDF = "PDF"
    DOCUMENT = "DOCUMENT"
    SPREADSHEET = "SPREADSHEET"
    PRESENTATION = "PRESENTATION"
    FORM = "FORM"
    FOLDER = "FOLDER"
    SHORTCUT = "SHORTCUT"
    DRAWING = "DRAWING"
    ARCHIVE = "ARCHIVE"
    DESIGN = "DESIGN"
    VECTOR = "VECTOR"
    CODE = "CODE"
    OTHER = "OTHER"
