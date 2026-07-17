"""Business operations for indexed media assets."""

from app.constants import AssetCategory
from app.database.models import File
from app.database.repository import FileRepository


class AssetService:
    """Provides business-level access to indexed assets.

    The service owns no database session and delegates persistence operations
    to ``FileRepository``. Future modules should depend on this service rather
    than querying repositories directly.

    Examples:
        repository = FileRepository()
        assets = AssetService(repository)
        videos = assets.list_videos()
    """

    def __init__(self, repository: FileRepository) -> None:
        """Initializes the service with its asset repository.

        Args:
            repository: Repository used to access indexed file records.
        """
        self.repository = repository

    def get_by_id(self, asset_id: int) -> File | None:
        """Returns an asset by its database ID.

        Args:
            asset_id: Primary key of the indexed asset.

        Returns:
            The matching asset, or ``None`` when it does not exist.
        """
        return self.repository.get_by_id(asset_id)

    def get_by_drive_id(self, drive_file_id: str) -> File | None:
        """Returns an asset by its Google Drive file ID.

        Args:
            drive_file_id: Google Drive identifier for the asset.

        Returns:
            The matching asset, or ``None`` when it does not exist.
        """
        return self.repository.get_by_drive_id(drive_file_id)

    def list_all(self) -> list[File]:
        """Returns every indexed asset.

        Returns:
            All indexed asset records.
        """
        return self.repository.get_all()

    def list_videos(self) -> list[File]:
        """Returns assets categorized as videos.

        Returns:
            Indexed video asset records.
        """
        return self.repository.get_by_category(AssetCategory.VIDEO.value)

    def list_images(self) -> list[File]:
        """Returns assets categorized as images.

        Returns:
            Indexed image asset records.
        """
        return self.repository.get_by_category(AssetCategory.IMAGE.value)

    def list_folders(self) -> list[File]:
        """Returns indexed folder records.

        Returns:
            Indexed assets marked as folders.
        """
        return self.repository.get_folders()

    def count_assets(self) -> int:
        """Returns the total number of indexed assets.

        Returns:
            Total indexed asset count.
        """
        return self.repository.count_all()

    def count_videos(self) -> int:
        """Returns the number of indexed video assets.

        Returns:
            Indexed video asset count.
        """
        return self.repository.count_by_category(AssetCategory.VIDEO.value)

    def count_images(self) -> int:
        """Returns the number of indexed image assets.

        Returns:
            Indexed image asset count.
        """
        return self.repository.count_by_category(AssetCategory.IMAGE.value)

    def exists(self, drive_file_id: str) -> bool:
        """Reports whether an indexed asset has a Google Drive file ID.

        Args:
            drive_file_id: Google Drive identifier to check.

        Returns:
            ``True`` when the asset exists; otherwise ``False``.
        """
        return self.repository.exists_by_drive_id(drive_file_id)
