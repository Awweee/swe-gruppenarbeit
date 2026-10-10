"""Pydantic-Model für die Pizzeriadaten."""

from typing import Annotated, Final

from loguru import logger
from pydantic import BaseModel, ConfigDict, StringConstraints

from pizzeria.entity import Pizzeria
from pizzeria.router.adresse_model import AdresseModel
from pizzeria.router.pizza_model import PizzaModel

__all__ = ["PizzeriaModel"]


class PizzeriaModel(BaseModel):
    """Pydantic-Model für die Pizzeriadaten einschließlich Beziehungen."""

    name: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    """Name der Pizzeria."""

    telefon: str | None = None
    """Telefonnummer."""

    email: str | None = None
    """E-Mail-Adresse."""

    adresse: AdresseModel
    """Zugehörige Adresse (1:1)."""

    pizzen: list[PizzaModel]
    """Angebotene Pizzen (1:N)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Pizza Napoli",
                "telefon": "0721 123456",
                "email": "info@pizza-napoli.de",
                "adresse": {
                    "strasse": "Kaiserstraße",
                    "hausnummer": "12a",
                    "plz": "76133",
                    "ort": "Karlsruhe",
                },
                "pizzen": [
                    {
                        "name": "Margherita",
                        "beschreibung": "Tomaten, Mozzarella, Basilikum",
                        "preis": "8.50",
                        "vegetarisch": True,
                    }
                ],
            },
        },
        strict=True,
        extra="forbid",
        frozen=True,
    )

    def to_pizzeria(self) -> Pizzeria:
        """Konvertierung in ein Pizzeria-Objekt für SQLAlchemy.

        :return: Pizzeria-Objekt für SQLAlchemy
        :rtype: Pizzeria
        """
        logger.debug("self={}", self)

        pizzeria: Final = Pizzeria(
            name=self.name,
            telefon=self.telefon,
            email=self.email,
        )

        pizzeria.adresse = self.adresse.to_adresse()

        pizzeria.pizzen = [
            pizza_model.to_pizza() for pizza_model in self.pizzen
        ]

        logger.debug("pizzeria={}", pizzeria)

        return pizzeria
