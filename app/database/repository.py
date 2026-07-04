from datetime import datetime

from sqlalchemy import select

from app.database.models import File
from app.database.session import SessionLocal


class FileRepository:

    def __init__(self):
        self.session = SessionLocal()

    def get_by_drive_id(self, drive_file_id: str):
        return self.session.scalar(
            select(File).where(
                File.drive_file_id == drive_file_id
            )
        )

    def add(self, file: File):
        self.session.add(file)
        self.session.commit()
        self.session.refresh(file)
        return file

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

        self.session.commit()
        self.session.refresh(existing)

        return existing

    def touch(self, file: File):
        file.last_seen = datetime.utcnow()
        file.is_deleted = False
        self.session.commit()

    def mark_all_deleted(self):

        files = self.get_all()

        for file in files:
            file.is_deleted = True

        self.session.commit()

    def restore(self, file: File):

        file.is_deleted = False
        file.last_seen = datetime.utcnow()

        self.session.commit()

    def get_all(self):
        return self.session.scalars(
            select(File)
        ).all()

    def close(self):
        self.session.close()