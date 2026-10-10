"""Entity-Klasse für die Adresse."""

from typing import TYPE_CHECKING, override

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pizzeria.entity.base import Base

if TYPE_CHECKING:
    from pizzeria.entity.pizzeria import Pizzeria


class Adresse(Base):
    """Entity-Klasse für die Adresse."""

    __tablename__ = "adresse"

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000, always=True),
        primary_key=True,
    )
    """Die generierte ID."""

    strasse: Mapped[str]
    """Die Straße."""

    hausnummer: Mapped[str]
    """Die Hausnummer."""

    plz: Mapped[str]
    """Die Postleitzahl."""

    ort: Mapped[str]
    """Der Ort."""

    pizzeria_id: Mapped[int] = mapped_column(
        ForeignKey("pizzeria.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    """ID der zugehörigen Pizzeria als eindeutiger Fremdschlüssel."""

    pizzeria: Mapped["Pizzeria"] = relationship(
        "Pizzeria",
        back_populates="adresse",
    )
    """Die zugehörige Pizzeria."""

    @override
    def __repr__(self) -> str:
        """Ausgabe der Adresse ohne zusätzliche Datenbankabfragen."""
        return (
            f"Adresse(id={self.id}, strasse={self.strasse}, "
            f"hausnummer={self.hausnummer}, plz={self.plz}, "
            f"ort={self.ort})"
        )
