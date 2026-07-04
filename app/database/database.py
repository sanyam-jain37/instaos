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
    """
    Create tables if they don't already exist.
    """

    from app.database import models

    Base.metadata.create_all(bind=engine)

    print("✅ Database ready!")