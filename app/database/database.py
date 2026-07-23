from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite:///data/instaos.db"


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)


def create_database():
    """Create all database tables if they don't already exist."""

    # Import models so SQLAlchemy registers them before create_all()
    from app.database import models as _models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    print("✅ Database ready!")