"""Pydantic-Model für die Pizzen."""

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from pizzeria.entity import Pizza

__all__ = ["PizzaModel"]


class PizzaModel(BaseModel):
    """Pydantic-Model für eine Pizza."""

    name: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    """Bezeichnung der Pizza."""

    beschreibung: str | None = None
    """Beschreibung der Pizza."""

    preis: Decimal = Field(
        gt=Decimal("0"),
        max_digits=10,
        decimal_places=2,
        strict=False,
    )
    """Preis der Pizza."""

    vegetarisch: bool = False
    """Kennzeichen für vegetarische Pizzen."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Margherita",
                "beschreibung": "Tomaten, Mozzarella, Basilikum",
                "preis": "8.50",
                "vegetarisch": True,
            },
        },
        strict=True,
        extra="forbid",
        frozen=True,
    )

    def to_pizza(self) -> Pizza:
        """Konvertierung in ein Pizza-Objekt für SQLAlchemy.

        :return: Pizza-Objekt für SQLAlchemy
        :rtype: Pizza
        """
        return Pizza(
            name=self.name,
            beschreibung=self.beschreibung,
            preis=self.preis,
            vegetarisch=self.vegetarisch,
        )
