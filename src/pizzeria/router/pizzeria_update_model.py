"""Pydantic-Model zum Aktualisieren von Pizzeriadaten."""

from typing import Annotated

from loguru import logger
from pydantic import BaseModel, ConfigDict, StringConstraints

from pizzeria.entity import Pizzeria
from pizzeria.router.adresse_model import AdresseModel
from pizzeria.router.pizza_model import PizzaModel

__all__ = ["pizzeriaUpdateModel"]


class pizzeriaUpdateModel(BaseModel):
    """Pydantic-Model zum Aktualisieren der Pizzeriadaten."""

    name: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    """Name der Pizzeria."""

    telefon: str | None = None
    """Telefonnummer."""

    email: str | None = None
    """E-Mail-Adresse."""

    adresse: AdresseModel | None = None

    pizzen: list[PizzaModel] | None = None

    username: str | None = None
    """Benutzername des Eigentümers."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Pizza Napoli",
                "telefon": "0721 123456",
                "email": "info@pizza-napoli.de",
                "username": "pizza-napoli",
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
        """Konvertierung in ein Pizzeria-Objekt für SQLAlchemy."""
        logger.debug("self={}", self)
        pizzeria = Pizzeria(
            name=self.name,
            telefon=self.telefon,
            email=self.email,
            username=self.username,
            adresse=self.adresse.to_adresse() if self.adresse is not None else None,
            pizzen=(
                [pizza_model.to_pizza() for pizza_model in self.pizzen]
                if self.pizzen is not None
                else []
            ),
        )
        logger.debug("pizzeria={}", pizzeria)
        return pizzeria
