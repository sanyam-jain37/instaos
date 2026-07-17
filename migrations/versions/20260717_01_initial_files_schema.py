"""Create the initial files schema.

Revision ID: 20260717_01
Revises:
Create Date: 2026-07-17

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260717_01"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Create a fresh schema or safely baseline an existing InstaOS database."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("files"):
        return

    op.create_table(
        "files",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("drive_file_id", sa.String(), nullable=False),
        sa.Column("parent_drive_id", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("extension", sa.String(), nullable=True),
        sa.Column("mime_type", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("full_path", sa.String(), nullable=False),
        sa.Column("folder_name", sa.String(), nullable=True),
        sa.Column("drive_url", sa.String(), nullable=True),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("created_time", sa.DateTime(), nullable=True),
        sa.Column("modified_time", sa.DateTime(), nullable=True),
        sa.Column("md5_checksum", sa.String(), nullable=True),
        sa.Column("is_folder", sa.Boolean(), nullable=False),
        sa.Column("is_shortcut", sa.Boolean(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("last_seen", sa.DateTime(), nullable=False),
        sa.Column("indexed_at", sa.DateTime(), nullable=False),
        sa.Column("last_scanned", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("drive_file_id"),
    )
    op.create_index("ix_files_drive_file_id", "files", ["drive_file_id"])
    op.create_index("ix_files_category", "files", ["category"])


def downgrade() -> None:
    """Do not drop a table that may have existed before Alembic adoption."""
    raise NotImplementedError(
        "The InstaOS baseline migration is intentionally non-reversible. "
        "Restore a database backup instead."
    )
