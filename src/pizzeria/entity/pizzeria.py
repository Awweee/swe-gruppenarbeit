"""Entity-Klasse für Pizzeria."""

from typing import TYPE_CHECKING, override

from sqlalchemy import Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pizzeria.entity.base import Base

if TYPE_CHECKING:
    from pizzeria.entity.adresse import Adresse
    from pizzeria.entity.pizza import Pizza


class Pizzeria(Base):
    """Entity-Klasse für Pizzeriadaten."""

    __tablename__ = "pizzeria"

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000, always=True),
        primary_key=True,
    )
    """Die generierte ID."""

    name: Mapped[str]
    """Der Name der Pizzeria."""

    telefon: Mapped[str | None]
    """Die optionale Telefonnummer."""

    email: Mapped[str | None] = mapped_column(unique=True)
    """Die optionale eindeutige E-Mail-Adresse."""

    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-one
    adresse: Mapped["Adresse | None"] = relationship(
        "Adresse",
        back_populates="pizzeria",
        uselist=False,
        cascade="save-update, delete",
    )
    """Die in einer 1:1-Beziehung referenzierte Adresse."""

    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many
    pizzen: Mapped[list["Pizza"]] = relationship(
        "Pizza",
        back_populates="pizzeria",
        cascade="save-update, delete",
    )
    """Die in einer 1:N-Beziehung referenzierten Pizzen."""

    @override
    def __repr__(self) -> str:
        """Ausgabe der Pizzeria ohne zusätzliche Datenbankabfragen."""
        return (
            f"Pizzeria(id={self.id}, name={self.name}, "
            f"telefon={self.telefon}, email={self.email})"
        )
