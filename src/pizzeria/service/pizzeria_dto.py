"""DTO-Klasse für Pizzeriadaten."""

from dataclasses import dataclass
from typing import Self

from pizzeria.entity.pizzeria import Pizzeria
from pizzeria.service.adresse_dto import AdresseDTO

__all__ = ["PizzeriaDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
class PizzeriaDTO:
    """DTO-Klasse für gelesene oder gespeicherte Pizzeriadaten."""

    id: int
    """Generierte ID der Pizzeria."""

    name: str
    """Name der Pizzeria."""

    telefon: str | None
    """Telefonnummer der Pizzeria."""

    adresse: AdresseDTO | None
    """Adresse der Pizzeria."""

    @classmethod
    def from_pizzeria(cls, pizzeria: Pizzeria) -> Self:
        """Initialisierung von PizzeriaDTO durch ein Entity-Objekt.

        :param pizzeria: Pizzeria-Objekt von SQLAlchemy
        :return: PizzeriaDTO mit den Pizzeriadaten
        :rtype: PizzeriaDTO
        """
        return cls(
            id=pizzeria.id if pizzeria.id is not None else -1,
            name=pizzeria.name,
            telefon=pizzeria.telefon,
            adresse=(
                AdresseDTO.from_adresse(pizzeria.adresse)
                if pizzeria.adresse is not None
                else None
            ),
        )
