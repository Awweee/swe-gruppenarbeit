"""Modul für die REST-Schnittstelle einschließlich Validierung."""

from collections.abc import Sequence

from pizzeria.router.adresse_model import AdresseModel
from pizzeria.router.pizza_model import PizzaModel
from pizzeria.router.pizzeria_model import PizzeriaModel
from pizzeria.router.pizzeria_write_router import (
    delete_by_id,
    pizzeria_write_router,
    post,
    put,
)
from pizzeria.router.router import (
    get,
    get_by_id,
    pizzeria_router,
    query,
)

__all__: Sequence[str] = [
    "AdresseModel",
    "PizzaModel",
    "PizzeriaModel",
    "PizzeriaInput",
    "pizzeria_router",
    "delete_by_id",
    "get",
    "get_by_id",
    "pizzeria_router",
    "pizzeria_write_router",
    "post",
    "put",
    "query",
]
