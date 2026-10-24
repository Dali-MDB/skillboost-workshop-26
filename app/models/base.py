from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base — inherit all SQLAlchemy models from this."""
    pass
