
"""Repository für persistente Pizzeriadaten."""

from typing import Final

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from pizzeria.entity import Pizzeria

__all__ = ["PizzeriaRepository"]


class PizzeriaRepository:
    """Repository-Klasse mit CRUD-Methoden für die Entity-Klasse Pizzeria."""

    def find_by_id(
        self,
        pizzeria_id: int | None,
        session: Session,
    ) -> Pizzeria | None:
        """Suche mit der Pizzeria-ID.

        :param pizzeria_id: ID der gesuchten Pizzeria
        :param session: Session für SQLAlchemy
        :return: Die gefundene Pizzeria oder None
        :rtype: Pizzeria | None
        """
        logger.debug("pizzeria_id={}", pizzeria_id)

        if pizzeria_id is None:
            return None

        statement: Final = (
            select(Pizzeria)
            .options(
                joinedload(Pizzeria.adresse),
                selectinload(Pizzeria.pizzen),
            )
            .where(Pizzeria.id == pizzeria_id)
        )

        pizzeria: Final = session.scalar(statement)

        logger.debug("pizzeria={}", pizzeria)
        return pizzeria

    def find_all(
        self,
        session: Session,
    ) -> list[Pizzeria]:
        """Alle Pizzerien suchen.

        :param session: Session für SQLAlchemy
        :return: Liste aller Pizzerien
        :rtype: list[Pizzeria]
        """
        logger.debug("Alle Pizzerien suchen")

        statement: Final = (
            select(Pizzeria)
            .options(
                joinedload(Pizzeria.adresse),
                selectinload(Pizzeria.pizzen),
            )
            .order_by(Pizzeria.id)
        )

        pizzerien: Final = list(session.scalars(statement).all())

        logger.debug("pizzerien={}", pizzerien)
        return pizzerien

    def create(
        self,
        pizzeria: Pizzeria,
        session: Session,
    ) -> Pizzeria:
        """Eine neue Pizzeria persistieren.

        :param pizzeria: Neue Pizzeria
        :param session: Session für SQLAlchemy
        :return: Persistierte Pizzeria mit generierter ID
        :rtype: Pizzeria
        """
        logger.debug("pizzeria={}", pizzeria)

        session.add(pizzeria)
        session.flush()

        logger.debug("pizzeria={}", pizzeria)
        return pizzeria

    def delete_by_id(
        self,
        pizzeria_id: int,
        session: Session,
    ) -> bool:
        """Eine Pizzeria anhand ihrer ID löschen.

        :param pizzeria_id: ID der zu löschenden Pizzeria
        :param session: Session für SQLAlchemy
        :return: True, falls die Pizzeria gefunden und gelöscht wurde
        :rtype: bool
        """
        logger.debug("pizzeria_id={}", pizzeria_id)

        pizzeria: Final = session.get(Pizzeria, pizzeria_id)

        if pizzeria is None:
            return False

        session.delete(pizzeria)
        session.flush()

        logger.debug("Pizzeria mit ID {} gelöscht", pizzeria_id)
        return True
