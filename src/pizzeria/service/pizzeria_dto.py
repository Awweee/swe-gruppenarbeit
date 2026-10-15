
from pizzeria.entity.pizzeria import Pizzeria


class PizzeriaDTO:
    """Data Transfer Object für Pizzerien."""

    id: int
    name: str
    email: str
    telefon: str

    def from_pizzeria(cls, pizzeria: Pizzeria) -> PizzeriaDTO:
        """Erstellt ein DTO aus einer Pizzeria-Entity."""
        return PizzeriaDTO(
            id=pizzeria.id if pizzeria.id is not None else -1,
            name=pizzeria.name,
            email=pizzeria.email,
            telefon=pizzeria.telefon,
        )
