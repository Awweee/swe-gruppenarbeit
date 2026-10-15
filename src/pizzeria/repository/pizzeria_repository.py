"""Repository für persistente Pizzeriadaten."""

from collections.abc import Sequence
from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from pizzeria.entity.pizzeria import Pizzeria
from pizzeria.repository.pageable import Pageable
from pizzeria.repository.pizzeria_suchparameter import PizzeriaSuchparameter
from pizzeria.repository.slice import Slice

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
            .options(joinedload(Pizzeria.adresse))
            .where(Pizzeria.id == pizzeria_id)
        )

        pizzeria: Final = session.scalar(statement)

        logger.debug("{}", pizzeria)
        return pizzeria

    def find(
        self,
        suchparameter: PizzeriaSuchparameter | None,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Pizzeria]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter oder None
        :param pageable: Anzahl Datensätze und Seitennummer
        :param session: Session für SQLAlchemy
        :return: Gefundene Pizzerien als Slice
        :rtype: Slice[Pizzeria]
        """
        logger.debug("suchparameter={}", suchparameter)

        if suchparameter is None or suchparameter.is_empty():
            return self._find_all(
                pageable=pageable,
                session=session,
            )

        if suchparameter.name is not None:
            pizzerien: Final = self._find_by_name(
                teil=suchparameter.name,
                pageable=pageable,
                session=session,
            )

            logger.debug("pizzerien={}", pizzerien)
            return pizzerien

        return Slice(content=(), total_elements=0)

    def _find_all(
        self,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Pizzeria]:
        """Alle Pizzerien mit Pagination suchen.

        :param pageable: Parameter für Pagination
        :param session: Session für SQLAlchemy
        :return: Gefundene Pizzerien als Slice
        :rtype: Slice[Pizzeria]
        """
        logger.debug("aufgerufen")

        offset: Final = pageable.number * pageable.size

        statement: Final = select(Pizzeria).options(
            joinedload(Pizzeria.adresse)
        )

        if pageable.size != 0:
            statement = statement.limit(pageable.size).offset(offset)

        pizzerien: Final = session.scalars(statement).all()

        anzahl: Final = self._count_all_rows(session=session)

        pizzeria_slice: Final = Slice(
            content=tuple(pizzerien),
            total_elements=anzahl,
        )

        logger.debug("pizzeria_slice={}", pizzeria_slice)
        return pizzeria_slice

    def _count_all_rows(
        self,
        session: Session,
    ) -> int:
        """Anzahl aller Pizzerien ermitteln.

        :param session: Session für SQLAlchemy
        :return: Anzahl aller Pizzerien
        :rtype: int
        """
        statement: Final = select(func.count()).select_from(Pizzeria)

        count: Final = session.scalar(statement)

        return count if count is not None else 0

    def _find_by_name(
        self,
        teil: str,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Pizzeria]:
        """Pizzerien anhand eines Namensteils suchen.

        :param teil: Teilstring des Pizzerianamens
        :param pageable: Parameter für Pagination
        :param session: Session für SQLAlchemy
        :return: Gefundene Pizzerien als Slice
        :rtype: Slice[Pizzeria]
        """
        logger.debug("teil={}", teil)

        offset: Final = pageable.number * pageable.size

        statement = (
            select(Pizzeria)
            .options(joinedload(Pizzeria.adresse))
            .where(Pizzeria.name.ilike(f"%{teil}%"))
        )

        if pageable.size != 0:
            statement = statement.limit(pageable.size).offset(offset)

        pizzerien: Final = session.scalars(statement).all()

        anzahl: Final = self._count_rows_name(
            teil=teil,
            session=session,
        )

        pizzeria_slice: Final = Slice(
            content=tuple(pizzerien),
            total_elements=anzahl,
        )

        logger.debug("pizzeria_slice={}", pizzeria_slice)
        return pizzeria_slice

    def _count_rows_name(
        self,
        teil: str,
        session: Session,
    ) -> int:
        """Anzahl der Pizzerien mit passendem Namen ermitteln.

        :param teil: Teilstring des Pizzerianamens
        :param session: Session für SQLAlchemy
        :return: Anzahl der gefundenen Pizzerien
        :rtype: int
        """
        statement: Final = (
            select(func.count())
            .select_from(Pizzeria)
            .where(Pizzeria.name.ilike(f"%{teil}%"))
        )

        count: Final = session.scalar(statement)

        return count if count is not None else 0

    def create(
        self,
        pizzeria: Pizzeria,
        session: Session,
    ) -> Pizzeria:
        """Speichere eine neue Pizzeria ab.

        :param pizzeria: Die Daten der neuen Pizzeria ohne ID
        :param session: Session für SQLAlchemy
        :return: Die neu angelegte Pizzeria mit generierter ID
        :rtype: Pizzeria
        """
        logger.debug(
            "pizzeria={}, pizzeria.adresse={}, pizzeria.pizzen={}",
            pizzeria,
            pizzeria.adresse,
            pizzeria.pizzen,
        )

        session.add(pizzeria)

        session.flush()

        logger.debug("pizzeria_id={}", pizzeria.id)

        return pizzeria

    def update(
        self,
        pizzeria: Pizzeria,
        session: Session,
    ) -> Pizzeria | None:
        """Aktualisiere eine Pizzeria.

        :param pizzeria: Die neuen Pizzeriadaten
        :param session: Session für SQLAlchemy
        :return: Aktualisierte Pizzeria oder None
        :rtype: Pizzeria | None
        """
        logger.debug("pizzeria={}", pizzeria)

        pizzeria_db: Final = self.find_by_id(
            pizzeria_id=pizzeria.id,
            session=session,
        )

        if pizzeria_db is None:
            return None

        pizzeria_db.name = pizzeria.name
        pizzeria_db.telefon = pizzeria.telefon

        session.flush()

        logger.debug("pizzeria_db={}", pizzeria_db)

        return pizzeria_db

    def delete_by_id(
        self,
        pizzeria_id: int,
        session: Session,
    ) -> None:
        """Lösche die Daten einer Pizzeria.

        :param pizzeria_id: ID der zu löschenden Pizzeria
        :param session: Session für SQLAlchemy
        """
        logger.debug("pizzeria_id={}", pizzeria_id)

        pizzeria: Final = self.find_by_id(
            pizzeria_id=pizzeria_id,
            session=session,
        )

        if pizzeria is None:
            return

        session.delete(pizzeria)

        logger.debug("Pizzeria geloescht")

    def find_namen(
        self,
        teil: str,
        session: Session,
    ) -> Sequence[str]:
        """Suche Pizzerianamen zu einem Teilstring.

        :param teil: Teilstring der gesuchten Namen
        :param session: Session für SQLAlchemy
        :return: Gefundene Pizzerianamen
        :rtype: Sequence[str]
        """
        logger.debug("teil={}", teil)

        statement: Final = (
            select(Pizzeria.name)
            .where(Pizzeria.name.ilike(f"%{teil}%"))
            .distinct()
        )

        namen: Final = session.scalars(statement).all()

        logger.debug("namen={}", namen)
        return namen
