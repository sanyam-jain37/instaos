
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.database import Base


class File(Base):
    """
    Represents a file or folder indexed from Google Drive.
    """

    __tablename__ = "files"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    drive_file_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    parent_drive_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    extension: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    mime_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    full_path: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    folder_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    drive_url: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    size: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    created_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    modified_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    md5_checksum: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    is_folder: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_shortcut: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    indexed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    last_scanned: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return (
            f"<File("
            f"name='{self.name}', "
            f"category='{self.category}', "
            f"mime='{self.mime_type}'"
            f")>"
        )