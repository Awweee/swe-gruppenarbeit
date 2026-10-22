"""Entity-Klasse für Pizzeria."""

from typing import TYPE_CHECKING, Self, override

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

    telefon: Mapped[str | None] = mapped_column(nullable=True)
    """Die optionale Telefonnummer."""

    name: Mapped[str]
    """Der Name der Pizzeria."""

    email: Mapped[str | None] = mapped_column(unique=True)
    """Die optionale eindeutige E-Mail-Adresse."""

    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-one
    adresse: Mapped[Adresse | None] = relationship(
        "Adresse",
        back_populates="pizzeria",
        uselist=False,
        cascade="save-update, delete",
    )
    """Die in einer 1:1-Beziehung referenzierte Adresse."""

    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many
    pizzen: Mapped[list[Pizza]] = relationship(
        "Pizza",
        back_populates="pizzeria",
        cascade="save-update, delete",
    )
    """Die in einer 1:N-Beziehung referenzierten Pizzen."""

    username: Mapped[str | None]
    """Der Benutzername für Login."""

    # https://docs.sqlalchemy.org/en/20/orm/versioning.html#simple-version-counting
    version: Mapped[int] = mapped_column(nullable=False, default=0)
    """Die Versionsnummer für optimistische Synchronisation."""

    # https://docs.sqlalchemy.org/en/20/orm/versioning.html#simple-version-counting
    __mapper_args__ = {"version_id_col": version}

    def set(self, pizzeria: Self) -> None:
        """Primitive Attributwerte überschreiben, z.B. vor DB-Update.

        :param pizzeria: Pizzeria-Objekt mit den aktuellen Daten
        """
        self.name = pizzeria.name
        self.telefon = pizzeria.telefon
        self.email = pizzeria.email

    @override
    def __repr__(self) -> str:
        """Ausgabe der Pizzeria ohne zusätzliche Datenbankabfragen."""
        return (
            f"Pizzeria(id={self.id}, version={self.version}, "
            f"name={self.name}, telefon={self.telefon}, "
            f"email={self.email}, username={self.username})"
        )
