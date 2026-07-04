from sqlalchemy.orm import sessionmaker

from app.database.database import engine

# Factory that creates new database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)