"""Repository für den lesenden und schreibenden Zugriff auf Pizzerien."""

from typing import Final

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from pizzeria.entity import Pizzeria
from pizzeria.repository.pageable import Pageable
from pizzeria.repository.slice import Slice
from pizzeria.repository.suchparameter import Suchparameter

__all__ = ["repository"]


class repository:
    """Basisklasse für Repository-Klassen."""

    def find_by_id(
        self,
        pizzeria_id: int | None,
        session: Session,
    ) -> Pizzeria | None:
        """Sucht eine Pizzeria anhand der ID."""
        logger.debug("Repository.find_by_id(pizzeria_id={})", pizzeria_id)

        if pizzeria_id is None:
            return None

        statement: Final = (
            select(Pizzeria)
            .where(Pizzeria.id == pizzeria_id)
        )

        pizzeria: Final = session.scalar(statement)
        logger.debug("{}", pizzeria)

        return pizzeria

    def find(
        self,
        suchparameter: Suchparameter,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Pizzeria]:
        """Sucht Pizzerien anhand der Suchparameter."""
        logger.debug(
            "Repository.find(suchparameter={}, pageable={})",
            suchparameter,
            pageable,
        )

        if suchparameter.is_empty():
            return self._find_all(pageable, session)

        if suchparameter.email is not None:
            pizzeria: Final = self._find_by_email(
                email=suchparameter.email,
                session=session,
            )

            return (
                Slice(content=(pizzeria,), total_elements=1)
                if pizzeria is not None
                else Slice(content=(), total_elements=0)
            )

        if suchparameter.name is not None:
            return self._find_by_name(
                teil=suchparameter.name,
                pageable=pageable,
                session=session,
            )

        return Slice(content=(), total_elements=0)

    def _find_all(
        self,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Pizzeria]:
        """Sucht alle Pizzerien mit Pagination."""
        logger.debug("Repository._find_all(pageable={})", pageable)

        statement: Final = (
            (
                select(Pizzeria)
                .options(joinedload(Pizzeria.pizzen))
                .offset(pageable.number * pageable.size)
                .limit(pageable.size)
            )
            if pageable.size != 0
            else select(Pizzeria).options(joinedload(Pizzeria.pizzen))
        )

        pizzerias: Final = session.scalars(statement).unique().all()
        logger.debug("{}", pizzerias)

        statement_count: Final = (
            select(func.count())
            .select_from(Pizzeria)
        )

        total_elements: Final = session.scalar(statement_count) or 0
        logger.debug("total_elements={}", total_elements)

        return Slice(
            content=tuple(pizzerias),
            total_elements=total_elements,
        )

    def _find_by_email(
        self,
        email: str,
        session: Session,
    ) -> Pizzeria | None:
        """Sucht eine Pizzeria anhand ihrer E-Mail-Adresse."""
        logger.debug("Repository._find_by_email(email={})", email)

        statement: Final = (
            select(Pizzeria)
            .where(func.lower(Pizzeria.email) == func.lower(email))
        )

        pizzeria: Final = session.scalar(statement)
        logger.debug("{}", pizzeria)

        return pizzeria

    def _find_by_name(
        self,
        teil: str,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Pizzeria]:
        """Sucht Pizzerien anhand eines Namensteils."""
        logger.debug(
            "Repository._find_by_name(teil={}, pageable={})",
            teil,
            pageable,
        )

        statement: Final = (
            (
                select(Pizzeria)
                .where(func.lower(Pizzeria.name).like(f"%{teil.lower()}%"))
                .offset(pageable.number * pageable.size)
                .limit(pageable.size)
            )
            if pageable.size != 0
            else select(Pizzeria).where(
                func.lower(Pizzeria.name).like(f"%{teil.lower()}%")
            )
        )

        pizzerias: Final = session.scalars(statement).all()
        logger.debug("{}", pizzerias)

        statement_count: Final = (
            select(func.count())
            .select_from(Pizzeria)
            .where(func.lower(Pizzeria.name).like(f"%{teil.lower()}%"))
        )

        total_elements: Final = session.scalar(statement_count) or 0
        logger.debug("total_elements={}", total_elements)

        return Slice(
            content=tuple(pizzerias),
            total_elements=total_elements,
        )

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

        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#adding-new-or-existing-items
        session.add(instance=pizzeria)

        # flush(), damit die ID aus der Sequence vor COMMIT
        # fuer Logging verfuegbar ist
        # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#flushing
        session.flush(objects=[pizzeria])

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
        :return: Die aktualisierte Pizzeria oder None,
                 falls keine Pizzeria mit der ID existiert
        :rtype: Pizzeria | None
        """
        logger.debug("{}", pizzeria)

        if (
            pizzeria_db := self.find_by_id(
                pizzeria_id=pizzeria.id,
                session=session,
            )
        ) is None:
            return None

        # session.add(pizzeria_db) nicht notwendig,
        # da bereits in der Session zugegriffen

        # CAVEAT: Die erhoehte Versionsnummer ist erst
        # nach COMMIT sichtbar

        logger.debug("{}", pizzeria_db)

        return pizzeria_db

    def delete_by_id(
        self,
        pizzeria_id: int,
        session: Session,
    ) -> None:
        """Lösche die Daten zu einer Pizzeria.

        :param pizzeria_id: Die ID der zu löschenden Pizzeria
        :param session: Session für SQLAlchemy
        """
        logger.debug("pizzeria_id={}", pizzeria_id)

        # delete(Pizzeria).where(Pizzeria.id == pizzeria_id) OHNE cascade
        # "walrus operator" https://peps.python.org/pep-0572
        if (
            pizzeria := self.find_by_id(
                pizzeria_id=pizzeria_id,
                session=session,
            )
        ) is None:
            return

        session.delete(pizzeria)

        logger.debug("ok")
