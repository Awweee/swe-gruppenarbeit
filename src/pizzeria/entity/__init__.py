"""Modul für die SQLAlchemy-Entities."""

from collections.abc import Sequence

from pizzeria.entity.adresse import Adresse
from pizzeria.entity.pizza import Pizza
from pizzeria.entity.pizzeria import Pizzeria

__all__: Sequence[str] = [
    "Adresse",
    "Pizza",
    "Pizzeria",
]
