"""Modul für die REST-Schnittstelle einschließlich Validierung."""

from collections.abc import Sequence

from pizzeria.router.adresse_model import AdresseModel
from pizzeria.router.pizza_model import PizzaModel
from pizzeria.router.pizzeria_model import PizzeriaModel

__all__: Sequence[str] = [
    "AdresseModel",
    "PizzaModel",
    "PizzeriaModel",
]
