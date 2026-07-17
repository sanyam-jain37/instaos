"""Search and filtering operations for indexed assets."""

from datetime import datetime

from app.constants import AssetCategory
from app.database.models import File
from app.database.repository import FileRepository


class SearchService:
    """Provides repository-backed searches over indexed assets.

    The service normalizes user-facing filter values and delegates all
    persistence queries to ``FileRepository``.
    """

    def __init__(self, repository: FileRepository) -> None:
        """Initializes the service with its asset repository.

        Args:
            repository: Repository used to query indexed file records.
        """
        self.repository = repository

    def search_by_name(self, name: str) -> list[File]:
        """Returns assets whose names contain the provided text.

        Args:
            name: Text to match within an asset name.

        Returns:
            Matching indexed asset records.
        """
        return self.repository.find_by_name(name)

    def search_by_extension(self, extension: str) -> list[File]:
        """Returns assets with the provided file extension.

        Args:
            extension: Extension with or without a leading period.

        Returns:
            Matching indexed asset records.
        """
        normalized_extension = extension.lower()
        if normalized_extension and not normalized_extension.startswith("."):
            normalized_extension = f".{normalized_extension}"

        return self.repository.get_by_extension(normalized_extension)

    def search_by_mime_type(self, mime_type: str) -> list[File]:
        """Returns assets with the provided MIME type.

        Args:
            mime_type: MIME type to match.

        Returns:
            Matching indexed asset records.
        """
        return self.repository.get_by_mime_type(mime_type.lower())

    def search_by_category(self, category: AssetCategory) -> list[File]:
        """Returns assets in the provided category.

        Args:
            category: Shared asset category to match.

        Returns:
            Matching indexed asset records.
        """
        return self.repository.get_by_category(category.value)

    def search_by_parent(self, parent_drive_id: str) -> list[File]:
        """Returns assets directly contained by a Google Drive folder.

        Args:
            parent_drive_id: Google Drive ID of the parent folder.

        Returns:
            Matching indexed asset records.
        """
        return self.repository.get_by_parent_drive_id(parent_drive_id)

    def search_recent(self, limit: int = 25) -> list[File]:
        """Returns the most recently modified indexed assets.

        Args:
            limit: Maximum number of assets to return.

        Returns:
            Indexed assets ordered by descending modification time.
        """
        return self.repository.get_recent(limit)

    def search_large_files(self, min_size: int) -> list[File]:
        """Returns assets at least as large as the provided size.

        Args:
            min_size: Minimum asset size in bytes.

        Returns:
            Matching indexed asset records.
        """
        return self.repository.get_by_minimum_size(min_size)

    def search_by_modified_after(self, date: datetime) -> list[File]:
        """Returns assets modified after the provided timestamp.

        Args:
            date: Exclusive lower bound for asset modification time.

        Returns:
            Matching indexed asset records.
        """
        return self.repository.get_modified_after(date)
