from datetime import datetime
from pathlib import Path

from app.database.models import File
from app.services.category_service import CategoryService


class MetadataService:

    @staticmethod
    def _parse_datetime(value):
        if not value:
            return None

        dt = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        # Store as timezone-naive UTC to match SQLite
        return dt.replace(tzinfo=None)

    @staticmethod
    def build_file(file_data: dict, current_path: str) -> File:

        mime = file_data.get("mimeType", "")
        name = file_data.get("name", "")

        extension = Path(name).suffix.lower()

        category = CategoryService.get_category(
            mime,
            name,
        )

        drive_url = (
            f"https://drive.google.com/file/d/"
            f"{file_data['id']}/view"
        )

        return File(
            drive_file_id=file_data["id"],
            parent_drive_id=file_data.get("parents", [None])[0],
            name=name,
            extension=extension,
            mime_type=mime,
            category=category,
            full_path=f"{current_path}/{name}",
            folder_name=current_path.split("/")[-1],
            drive_url=drive_url,
            size=int(file_data.get("size", 0)),
            md5_checksum=file_data.get("md5Checksum"),

            created_time=MetadataService._parse_datetime(
                file_data.get("createdTime")
            ),

            modified_time=MetadataService._parse_datetime(
                file_data.get("modifiedTime")
            ),

            is_folder=(
                mime == "application/vnd.google-apps.folder"
            ),

            is_shortcut=(
                mime == "application/vnd.google-apps.shortcut"
            ),
        )