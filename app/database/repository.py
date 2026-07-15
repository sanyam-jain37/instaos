from datetime import datetime

from sqlalchemy import select

from app.database.models import File
from app.database.session import SessionLocal


class FileRepository:

    def __init__(self):
        self.session = SessionLocal()
        self._buffer = []

    # -----------------------------
    # Query Methods
    # -----------------------------

    def get_by_drive_id(self, drive_file_id: str):
        return self.session.scalar(
            select(File).where(
                File.drive_file_id == drive_file_id
            )
        )

    def get_all(self):
        return self.session.scalars(
            select(File)
        ).all()

    def get_by_drive_id_map(self) -> dict[str, File]:
        """Load indexed files once for constant-time scanner lookups."""
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
