
from dataclasses import dataclass

import strawberry
from pizzeria.entity.pizzeria import Pizzeria
from pizzeria.service.adresse_dto import AdresseDTO
@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type(name="pizzeria")
class PizzeriaDTO:
    """Data Transfer Object für Pizzerien."""

    id: int
    version: int
    name: str
    email: str
    telefon: str
    adresse: AdresseDTO
    username: str | None

    @classmethod
    def from_pizzeria(cls, pizzeria: Pizzeria) -> PizzeriaDTO:
        """Erstellt ein DTO aus einer Pizzeria-Entity."""
        return cls(
            id=pizzeria.id if pizzeria.id is not None else -1,
            version=pizzeria.version if pizzeria.version is not None else "N/A",
            username=pizzeria.username,
            name=pizzeria.name,
            email=pizzeria.email,
            adresse=AdresseDTO.from_adresse(pizzeria.adresse),
            telefon=pizzeria.telefon,
        )
