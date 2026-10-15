"""Geschäftslogik zum Lesen von Pizzeriadaten."""

from typing import Final

from loguru import logger

from pizzeria.repository import (
    Pageable,
    PizzeriaRepository,
    PizzeriaSuchparameter,
    Session,
    Slice,
)
from pizzeria.service.exceptions import NotFoundError
from pizzeria.service.pizzeria_dto import PizzeriaDTO

__all__ = ["PizzeriaService"]


class PizzeriaService:
    """Service-Klasse mit Geschäftslogik für Pizzerien."""

    def __init__(self, repo: PizzeriaRepository) -> None:
        """Konstruktor mit abhängigem PizzeriaRepository."""
        self.repo: PizzeriaRepository = repo

    def find_by_id(self, pizzeria_id: int) -> PizzeriaDTO:
        """Suche mit der Pizzeria-ID.

        :param pizzeria_id: ID für die Suche
        :return: Die gefundene Pizzeria
        :rtype: PizzeriaDTO
        :raises NotFoundError: Falls keine Pizzeria gefunden wurde
        """
        logger.debug("pizzeria_id={}", pizzeria_id)

        with Session() as session:
            pizzeria: Final = self.repo.find_by_id(
                pizzeria_id=pizzeria_id,
                session=session,
            )

            if pizzeria is None:
                logger.debug("Keine Pizzeria mit ID {}", pizzeria_id)
                raise NotFoundError(pizzeria_id=pizzeria_id)

            pizzeria_dto: Final = PizzeriaDTO.from_pizzeria(pizzeria)

            session.commit()

        logger.debug("pizzeria_dto={}", pizzeria_dto)
        return pizzeria_dto

    def find(
        self,
        suchparameter: PizzeriaSuchparameter | None,
        pageable: Pageable,
    ) -> Slice[PizzeriaDTO]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter oder None
        :param pageable: Parameter für Pagination
        :return: Gefundene Pizzerien als Slice
        :rtype: Slice[PizzeriaDTO]
        """
        logger.debug(
            "suchparameter={}, pageable={}",
            suchparameter,
            pageable,
        )

        with Session() as session:
            pizzeria_slice: Final = self.repo.find(
                suchparameter=suchparameter,
                pageable=pageable,
                session=session,
            )

            pizzeria_dtos: Final = tuple(
                PizzeriaDTO.from_pizzeria(pizzeria)
                for pizzeria in pizzeria_slice.content
            )

            result: Final = Slice(
                content=pizzeria_dtos,
                total_elements=pizzeria_slice.total_elements,
            )

            session.commit()

        logger.debug("result={}", result)
        return result
