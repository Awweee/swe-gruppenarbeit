"""Dependencies für die REST-Schnittstelle."""

from typing import Annotated

from fastapi import Depends

from pizzeria.repository.pizzeria_repository import PizzeriaRepository
from pizzeria.service.pizzeria_service import PizzeriaService
from pizzeria.service.pizzeria_write_service import PizzeriaWriteService

__all__ = [
    "get_repository",
    "get_read_service",
    "get_write_service",
]


def get_repository() -> PizzeriaRepository:
    """Repository bereitstellen."""
    return PizzeriaRepository()


def get_read_service(
    repo: Annotated[PizzeriaRepository, Depends(get_repository)],
) -> PizzeriaService:
    """Service zum Lesen von Pizzeriadaten bereitstellen."""
    return PizzeriaService(repo=repo)


def get_write_service(
    repo: Annotated[PizzeriaRepository, Depends(get_repository)],
) -> PizzeriaWriteService:
    """Service zum Schreiben von Pizzeriadaten bereitstellen."""
    return PizzeriaWriteService(repo=repo)
