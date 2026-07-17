"""Statistics and summaries for indexed assets."""

from app.constants import AssetCategory
from app.database.models import File
from app.database.repository import FileRepository


class StatisticsService:
    """Provides repository-backed statistics for the indexed asset library."""

    def __init__(self, repository: FileRepository) -> None:
        """Initializes the service with its asset repository.

        Args:
            repository: Repository used to aggregate indexed file records.
        """
        self.repository = repository

    def summary(self) -> dict[str, int]:
        """Returns the primary statistics for the indexed asset library.

        Returns:
            A dictionary containing asset counts and total storage in bytes.
        """
        return {
            "total_assets": self.total_assets(),
            "total_videos": self.total_videos(),
            "total_images": self.total_images(),
            "total_folders": self.total_folders(),
            "total_deleted_assets": self.total_deleted_assets(),
            "total_storage_bytes": self.total_storage_bytes(),
        }

    def total_assets(self) -> int:
        """Returns the total number of indexed assets.

        Returns:
            Total indexed asset count.
        """
        return self.repository.count_all()

    def total_videos(self) -> int:
        """Returns the total number of indexed video assets.

        Returns:
            Indexed video asset count.
        """
        return self.repository.count_by_category(AssetCategory.VIDEO.value)

    def total_images(self) -> int:
        """Returns the total number of indexed image assets.

        Returns:
            Indexed image asset count.
        """
        return self.repository.count_by_category(AssetCategory.IMAGE.value)

    def total_folders(self) -> int:
        """Returns the total number of indexed folder records.

        Returns:
            Indexed folder count.
        """
        return self.repository.count_folders()

    def total_deleted_assets(self) -> int:
        """Returns the total number of soft-deleted indexed assets.

        Returns:
            Soft-deleted asset count.
        """
        return self.repository.count_deleted()

    def total_storage_bytes(self) -> int:
        """Returns the combined size of indexed assets in bytes.

        Returns:
            Total indexed storage in bytes.
        """
        return self.repository.sum_size()

    def largest_files(self, limit: int = 10) -> list[File]:
        """Returns the largest indexed assets.

        Args:
            limit: Maximum number of assets to return.

        Returns:
            Indexed assets ordered by descending size.
        """
        return self.repository.get_largest(limit)

    def recent_assets(self, limit: int = 20) -> list[File]:
        """Returns the most recently modified indexed assets.

        Args:
            limit: Maximum number of assets to return.

        Returns:
            Indexed assets ordered by descending modification time.
        """
        return self.repository.get_recent(limit)
