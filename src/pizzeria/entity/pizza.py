"""Entity-Klasse für Pizza."""

from decimal import Decimal
from typing import TYPE_CHECKING, override

from sqlalchemy import ForeignKey, Identity, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pizzeria.entity.base import Base

if TYPE_CHECKING:
    from pizzeria.entity.pizzeria import Pizzeria


class Pizza(Base):
    """Entity-Klasse für eine Pizza."""

    __tablename__ = "pizza"

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000, always=True),
        primary_key=True,
    )
    """Die generierte ID."""

    name: Mapped[str]
    """Der Name der Pizza."""

    beschreibung: Mapped[str | None]
    """Die optionale Beschreibung der Pizza."""

    preis: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    """Der Preis der Pizza."""

    vegetarisch: Mapped[bool] = mapped_column(default=False)
    """Kennzeichen für vegetarische Pizzen."""

    pizzeria_id: Mapped[int] = mapped_column(
        ForeignKey("pizzeria.id", ondelete="CASCADE"),
        nullable=False,
    )
    """ID der zugehörigen Pizzeria als Fremdschlüssel."""

    pizzeria: Mapped["Pizzeria"] = relationship(
        "Pizzeria",
        back_populates="pizzen",
    )
    """Die zugehörige Pizzeria."""

    @override
    def __repr__(self) -> str:
        """Ausgabe der Pizza ohne zusätzliche Datenbankabfragen."""
        return (
            f"Pizza(id={self.id}, name={self.name}, "
            f"preis={self.preis}, vegetarisch={self.vegetarisch})"
        )

