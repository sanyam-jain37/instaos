from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.database import models  # noqa: F401 - registers ORM tables with Base
from app.database.database import Base, DATABASE_URL


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Keep Alembic and the application pointed at the same database URL.
config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata


def ensure_sqlite_directory() -> None:
    """Allow `alembic upgrade head` to initialize a missing SQLite database."""
    if DATABASE_URL.startswith("sqlite:///"):
        Path(DATABASE_URL.removeprefix("sqlite:///")).parent.mkdir(
            parents=True,
            exist_ok=True,
        )


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    ensure_sqlite_directory()
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
