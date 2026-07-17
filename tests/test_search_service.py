from datetime import datetime
from unittest.mock import Mock

import pytest

from app.constants import AssetCategory
from app.database.models import File
from app.database.repository import FileRepository
from app.services.search_service import SearchService


@pytest.fixture
def repository() -> Mock:
    return Mock(spec=FileRepository)


@pytest.fixture
def service(repository: Mock) -> SearchService:
    return SearchService(repository)


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


def test_search_by_name_delegates_to_repository(
    service: SearchService,
    repository: Mock,
    asset: File,
) -> None:
    repository.find_by_name.return_value = [asset]

    assert service.search_by_name("video") == [asset]
    repository.find_by_name.assert_called_once_with("video")


def test_search_by_extension_normalizes_extension(
    service: SearchService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_by_extension.return_value = [asset]

    assert service.search_by_extension("MP4") == [asset]
    repository.get_by_extension.assert_called_once_with(".mp4")


def test_search_by_mime_type_normalizes_value(
    service: SearchService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_by_mime_type.return_value = [asset]

    assert service.search_by_mime_type("VIDEO/MP4") == [asset]
    repository.get_by_mime_type.assert_called_once_with("video/mp4")


def test_search_by_category_uses_category_value(
    service: SearchService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_by_category.return_value = [asset]

    assert service.search_by_category(AssetCategory.VIDEO) == [asset]
    repository.get_by_category.assert_called_once_with(AssetCategory.VIDEO.value)


def test_search_by_parent_delegates_to_repository(
    service: SearchService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_by_parent_drive_id.return_value = [asset]

    assert service.search_by_parent("parent-1") == [asset]
    repository.get_by_parent_drive_id.assert_called_once_with("parent-1")


def test_search_recent_uses_default_limit(
    service: SearchService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_recent.return_value = [asset]

    assert service.search_recent() == [asset]
    repository.get_recent.assert_called_once_with(25)


def test_search_large_files_delegates_to_repository(
    service: SearchService,
    repository: Mock,
    asset: File,
) -> None:
    repository.get_by_minimum_size.return_value = [asset]

    assert service.search_large_files(1_000_000) == [asset]
    repository.get_by_minimum_size.assert_called_once_with(1_000_000)


def test_search_by_modified_after_delegates_to_repository(
    service: SearchService,
    repository: Mock,
    asset: File,
) -> None:
    modified_after = datetime(2026, 7, 1)
    repository.get_modified_after.return_value = [asset]

    assert service.search_by_modified_after(modified_after) == [asset]
    repository.get_modified_after.assert_called_once_with(modified_after)
