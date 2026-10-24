from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from typing import Generator
from app.config import settings




engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Shared declarative base — inherit all SQLAlchemy models from this."""


def get_db() -> Generator[Session, None, None]:
    """the database dependency, use it as Depends(get_db)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()   #must be closed after