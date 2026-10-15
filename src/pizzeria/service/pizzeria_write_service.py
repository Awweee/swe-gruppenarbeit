"""Geschäftslogik zum Schreiben von Pizzeriadaten."""

from typing import Final

from loguru import logger

from pizzeria.entity.pizzeria import Pizzeria
from pizzeria.repository import PizzeriaRepository, Session
from pizzeria.service.exceptions import NotFoundError
from pizzeria.service.pizzeria_dto import PizzeriaDTO

__all__ = ["PizzeriaWriteService"]


class PizzeriaWriteService:
    """Service-Klasse mit Geschäftslogik für Pizzerien."""

    def __init__(self, repo: PizzeriaRepository) -> None:
        """Konstruktor mit abhängigem PizzeriaRepository."""
        self.repo: PizzeriaRepository = repo

    def create(self, pizzeria: Pizzeria) -> PizzeriaDTO:
        """Eine neue Pizzeria anlegen.

        :param pizzeria: Die neue Pizzeria ohne ID
        :return: Die neu angelegte Pizzeria mit generierter ID
        :rtype: PizzeriaDTO
        """
        logger.debug(
            "pizzeria={}, adresse={}, pizzen={}",
            pizzeria,
            pizzeria.adresse,
            pizzeria.pizzen,
        )

        with Session() as session:
            pizzeria_db: Final = self.repo.create(
                pizzeria=pizzeria,
                session=session,
            )

            pizzeria_dto: Final = PizzeriaDTO.from_pizzeria(pizzeria_db)

            session.commit()

        logger.debug("pizzeria_dto={}", pizzeria_dto)
        return pizzeria_dto

    def update(
        self,
        pizzeria: Pizzeria,
        pizzeria_id: int,
    ) -> PizzeriaDTO:
        """Daten einer Pizzeria ändern.

        :param pizzeria: Die neuen Pizzeriadaten
        :param pizzeria_id: ID der zu aktualisierenden Pizzeria
        :return: Die aktualisierte Pizzeria
        :rtype: PizzeriaDTO
        :raises NotFoundError: Falls die Pizzeria nicht existiert
        """
        logger.debug(
            "pizzeria_id={}, pizzeria={}",
            pizzeria_id,
            pizzeria,
        )

        with Session() as session:
            pizzeria_db: Final = self.repo.find_by_id(
                pizzeria_id=pizzeria_id,
                session=session,
            )

            if pizzeria_db is None:
                raise NotFoundError(pizzeria_id=pizzeria_id)

            pizzeria_db.name = pizzeria.name
            pizzeria_db.telefon = pizzeria.telefon

            pizzeria_updated: Final = self.repo.update(
                pizzeria=pizzeria_db,
                session=session,
            )

            if pizzeria_updated is None:
                raise NotFoundError(pizzeria_id=pizzeria_id)

            pizzeria_dto: Final = PizzeriaDTO.from_pizzeria(
                pizzeria_updated
            )

            session.commit()

        logger.debug("pizzeria_dto={}", pizzeria_dto)
        return pizzeria_dto

    def delete_by_id(self, pizzeria_id: int) -> None:
        """Eine Pizzeria anhand ihrer ID löschen.

        :param pizzeria_id: ID der zu löschenden Pizzeria
        """
        logger.debug("pizzeria_id={}", pizzeria_id)

        with Session() as session:
            self.repo.delete_by_id(
                pizzeria_id=pizzeria_id,
                session=session,
            )

            session.commit()

        logger.debug("Pizzeria mit ID {} gelöscht", pizzeria_id)
