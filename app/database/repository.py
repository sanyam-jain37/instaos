from datetime import datetime

from sqlalchemy import func, select

from app.database.models import File
from app.database.session import SessionLocal


class FileRepository:

    def __init__(self):
        self.session = SessionLocal()
        self._buffer = []

    # -----------------------------
    # Query Methods
    # -----------------------------

    def get_by_id(self, asset_id: int) -> File | None:
        return self.session.get(File, asset_id)

    def get_by_drive_id(self, drive_file_id: str) -> File | None:
        return self.session.scalar(
            select(File).where(
                File.drive_file_id == drive_file_id
            )
        )

    def get_all(self) -> list[File]:
        return self.session.scalars(
            select(File)
        ).all()

    def get_by_category(self, category: str) -> list[File]:
        return self.session.scalars(
            select(File).where(File.category == category)
        ).all()

    def find_by_name(self, name: str) -> list[File]:
        return self.session.scalars(
            select(File).where(File.name.ilike(f"%{name}%"))
        ).all()

    def get_by_extension(self, extension: str) -> list[File]:
        return self.session.scalars(
            select(File).where(File.extension == extension)
        ).all()

    def get_by_mime_type(self, mime_type: str) -> list[File]:
        return self.session.scalars(
            select(File).where(File.mime_type == mime_type)
        ).all()

    def get_by_parent_drive_id(self, parent_drive_id: str) -> list[File]:
        return self.session.scalars(
            select(File).where(File.parent_drive_id == parent_drive_id)
        ).all()

    def get_recent(self, limit: int) -> list[File]:
        return self.session.scalars(
            select(File)
            .order_by(File.modified_time.desc())
            .limit(limit)
        ).all()

    def get_by_minimum_size(self, min_size: int) -> list[File]:
        return self.session.scalars(
            select(File).where(File.size >= min_size)
        ).all()

    def get_modified_after(self, date: datetime) -> list[File]:
        return self.session.scalars(
            select(File).where(File.modified_time > date)
        ).all()

    def get_folders(self) -> list[File]:
        return self.session.scalars(
            select(File).where(File.is_folder.is_(True))
        ).all()

    def count_all(self) -> int:
        return self.session.scalar(
            select(func.count()).select_from(File)
        ) or 0

    def count_by_category(self, category: str) -> int:
        return self.session.scalar(
            select(func.count())
            .select_from(File)
            .where(File.category == category)
        ) or 0

    def exists_by_drive_id(self, drive_file_id: str) -> bool:
        return self.session.scalar(
            select(File.id)
            .where(File.drive_file_id == drive_file_id)
            .limit(1)
        ) is not None

    def get_by_drive_id_map(self) -> dict[str, File]:
        """Build the once-per-scan cache used for constant-time lookups."""
        return {
            file.drive_file_id: file
            for file in self.get_all()
        }

    # -----------------------------
    # Batch Insert
    # -----------------------------

    def add_to_buffer(self, file: File):
        self._buffer.append(file)

    def commit_buffer(self):
        """Persist buffered inserts and staged ORM updates in one transaction."""
        if not self._buffer and not self.session.dirty:
            return

        try:
            if self._buffer:
                self.session.add_all(self._buffer)

            self.session.commit()
            self._buffer.clear()
        except Exception:
            self.session.rollback()
            raise

    # -----------------------------
    # Single Insert (Legacy)
    # -----------------------------

    def add(self, file: File):

        self.session.add(file)
        self.session.commit()
        self.session.refresh(file)

        return file

    # -----------------------------
    # Update
    # -----------------------------

    def update(self, existing: File, new: File):

        existing.name = new.name
        existing.extension = new.extension
        existing.mime_type = new.mime_type
        existing.category = new.category
        existing.full_path = new.full_path
        existing.folder_name = new.folder_name
        existing.drive_url = new.drive_url
        existing.size = new.size
        existing.created_time = new.created_time
        existing.modified_time = new.modified_time
        existing.md5_checksum = new.md5_checksum
        existing.is_folder = new.is_folder
        existing.is_shortcut = new.is_shortcut

        existing.last_seen = datetime.utcnow()
        existing.is_deleted = False

        return existing

    # -----------------------------
    # Sync Helpers
    # -----------------------------

    def touch(self, file: File):

        file.last_seen = datetime.utcnow()
        file.is_deleted = False

        self.session.commit()

    def mark_all_deleted(self):

        for file in self.get_all():
            file.is_deleted = True

        self.session.commit()

    def restore(self, file: File):

        file.is_deleted = False
        file.last_seen = datetime.utcnow()

        self.session.commit()

    # -----------------------------
    # Cleanup
    # -----------------------------

    def close(self):

        if self._buffer:
            self.commit_buffer()

        self.session.close()
