from unittest.mock import Mock, call

import pytest

from app.constants import AssetCategory
from app.database.models import File
from app.database.repository import FileRepository
from app.services.statistics_service import StatisticsService


@pytest.fixture
def repository() -> Mock:
    return Mock(spec=FileRepository)


@pytest.fixture
def service(repository: Mock) -> StatisticsService:
    return StatisticsService(repository)


@pytest.fixture
def asset() -> File:
    return File(
        id=1,
        drive_file_id="drive-file-1",
        name="video.mp4",
        mime_type="video/mp4",
        category=AssetCategory.VIDEO.value,
        full_path="My Drive/video.mp4",
        size=1_000_000,
    )


def test_summary_returns_primary_statistics(
    service: StatisticsService,
    repository: Mock,
) -> None:
    repository.count_all.return_value = 12
    repository.count_by_category.side_effect = [4, 3]
    repository.count_folders.return_value = 2
    repository.count_deleted.return_value = 1
    repository.sum_size.return_value = 3_000_000

    assert service.summary() == {
        "total_assets": 12,
        "total_videos": 4,
        "total_images": 3,
        "total_folders": 2,
        "total_deleted_assets": 1,
        "total_storage_bytes": 3_000_000,
    }
    repository.count_all.assert_called_once_with()
    assert repository.count_by_category.call_args_list == [
        call(AssetCategory.VIDEO.value),
        call(AssetCategory.IMAGE.value),
    ]
    repository.count_folders.assert_called_once_with()
    repository.count_deleted.assert_called_once_with()
    repository.sum_size.assert_called_once_with()


def test_total_assets_delegates_to_repository(
    service: StatisticsService,
    repository: Mock,
) -> None:
    repository.count_all.return_value = 12

    assert service.total_assets() == 12
    repository.count_all.assert_called_once_with()


def test_total_videos_uses_video_category(
    service: StatisticsService,
    repository: Mock,
) -> None:
    repository.count_by_category.return_value = 4

    assert service.total_videos() == 4
    repository.count_by_category.assert_called_once_with(AssetCategory.VIDEO.value)


def test_total_images_uses_image_category(
    service: StatisticsService,
    repository: Mock,
) -> None:
    repository.count_by_category.return_value = 3

    assert service.total_images() == 3
    repository.count_by_category.assert_called_once_with(AssetCategory.IMAGE.value)


def test_total_folders_delegates_to_repository(
    service: StatisticsService,
    repository: Mock,
) -> None:
    repository.count_folders.return_value = 2

    assert service.total_folders() == 2
    repository.count_folders.assert_called_once_with()


def test_total_deleted_assets_delegates_to_repository(
    service: StatisticsService,
    repository: Mock,
) -> None:
    repository.count_deleted.return_value = 1

    assert service.total_deleted_assets() == 1
    repository.count_deleted.assert_called_once_with()


def test_total_storage_bytes_delegates_to_repository(
    service: StatisticsService,
    repository: Mock,
) -> None:
    repository.sum_size.return_value = 3_000_000

    assert service.total_storage_bytes() == 3_000_000
    repository.sum_size.assert_called_once_with()


def test_largest_files_uses_default_limit(
    service: StatisticsService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_largest.return_value = [asset]

    assert service.largest_files() == [asset]
    repository.get_largest.assert_called_once_with(10)


def test_recent_assets_uses_default_limit(
    service: StatisticsService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_recent.return_value = [asset]

    assert service.recent_assets() == [asset]
    repository.get_recent.assert_called_once_with(20)
