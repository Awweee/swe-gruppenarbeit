"""Basisklasse für die SQLAlchemy-Entities."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Gemeinsame Basisklasse für die Entity-Klassen."""