from unittest.mock import Mock

import pytest

from app.database.models import File
from app.database.repository import FileRepository
from app.constants import AssetCategory
from app.services.asset_service import AssetService


@pytest.fixture
def repository() -> Mock:
    return Mock(spec=FileRepository)


@pytest.fixture
def service(repository: Mock) -> AssetService:
    return AssetService(repository)


@pytest.fixture
def asset() -> File:
    return File(
        id=1,
        drive_file_id="drive-file-1",
        name="video.mp4",
        mime_type="video/mp4",
        category=AssetCategory.VIDEO.value,
        full_path="My Drive/video.mp4",
    )


def test_get_by_id_returns_repository_result(
    service: AssetService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_by_id.return_value = asset

    assert service.get_by_id(1) is asset
    repository.get_by_id.assert_called_once_with(1)


def test_get_by_id_returns_none_when_missing(
    service: AssetService,
    repository: Mock,
) -> None:
    repository.get_by_id.return_value = None

    assert service.get_by_id(99) is None
    repository.get_by_id.assert_called_once_with(99)


def test_get_by_drive_id_returns_none_when_missing(
    service: AssetService,
    repository: Mock,
) -> None:
    repository.get_by_drive_id.return_value = None

    assert service.get_by_drive_id("missing") is None
    repository.get_by_drive_id.assert_called_once_with("missing")


def test_list_all_delegates_to_repository(
    service: AssetService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_all.return_value = [asset]

    assert service.list_all() == [asset]
    repository.get_all.assert_called_once_with()


def test_list_videos_filters_by_video_category(
    service: AssetService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_by_category.return_value = [asset]

    assert service.list_videos() == [asset]
    repository.get_by_category.assert_called_once_with(AssetCategory.VIDEO.value)


def test_list_images_filters_by_image_category(
    service: AssetService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_by_category.return_value = [asset]

    assert service.list_images() == [asset]
    repository.get_by_category.assert_called_once_with(AssetCategory.IMAGE.value)


def test_list_folders_delegates_to_repository(
    service: AssetService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_folders.return_value = [asset]

    assert service.list_folders() == [asset]
    repository.get_folders.assert_called_once_with()


def test_count_assets_delegates_to_repository(
    service: AssetService,
    repository: Mock,
) -> None:
    repository.count_all.return_value = 5

    assert service.count_assets() == 5
    repository.count_all.assert_called_once_with()


def test_count_videos_filters_by_video_category(
    service: AssetService,
    repository: Mock,
) -> None:
    repository.count_by_category.return_value = 3

    assert service.count_videos() == 3
    repository.count_by_category.assert_called_once_with(AssetCategory.VIDEO.value)


def test_count_images_filters_by_image_category(
    service: AssetService,
    repository: Mock,
) -> None:
    repository.count_by_category.return_value = 2

    assert service.count_images() == 2
    repository.count_by_category.assert_called_once_with(AssetCategory.IMAGE.value)


@pytest.mark.parametrize(
    ("repository_result", "expected"),
    [(True, True), (False, False)],
)
def test_exists_delegates_to_repository(
    service: AssetService,
    repository: Mock,
    repository_result: bool,
    expected: bool,
) -> None:
    repository.exists_by_drive_id.return_value = repository_result

    assert service.exists("drive-file-1") is expected
    repository.exists_by_drive_id.assert_called_once_with("drive-file-1")
