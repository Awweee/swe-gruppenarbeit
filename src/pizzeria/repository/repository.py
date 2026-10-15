__all__: list[str]= ["Repository"]

from typing import Final
lazy from collections.abc import Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from pizzeria.entity import Pizzeria
from pizzeria.repository.pageable import Pageable
from pizzeria.repository.suchparameter import Suchparameter
from pizzeria.repository.slice import Slice

class Repository:
    """Basisklasse für Repository-Klassen."""

    def find_by_id(self, pizzeria_id: int | None, session: Session) -> Pizzeria | None:
        logger.debug(f"Repository.find_by_id(pizzeria_id={pizzeria_id})")
        """Sucht eine Pizzeria anhand der ID."""
        if pizzeria_id is None:
            return None

        statement: Final = (
            select(Pizzeria)
            .where(Pizzeria.id == pizzeria_id)
        )
        pizzeria: Final = session.scalar(statement)
        logger.debug("{}", pizzeria)
        return pizzeria

    def find(self, suchparameter: Suchparameter, pageable: Pageable, session: Session) -> Slice[Pizzeria]:
        logger.debug(f"Repository.find(suchparameter={suchparameter})")
        if suchparameter is None or suchparameter.is_empty():
            return self._find_all(pageable, session)

        if suchparameter.email is not None:
            pizzeria = self._find_by_email(email=suchparameter.email, session=session)
            return (Slice (content=(pizzeria,), total_elements=1)
                    if pizzeria is not None
                    else Slice(content=(), total_elements=0))
        if suchparameter.name is not None:
            pizzeria = self._find_by_name(
                teil=suchparameter.name,
                pageable=pageable,
                session=session,
            )
            logger.debug("{}", pizzeria)
            return Slice(content=(pizzeria,), total_elements=1)

        return Slice(content=(), total_elements=0)

    def _find_all(self, pageable: Pageable, session: Session) -> Slice[Pizzeria]:
        logger.debug(f"Repository._find_all(pageable={pageable})")
        statement: Final = (
            (
            select(Pizzeria)
            .options(joinedload(Pizzeria.pizzas))
            .offset(pageable.offset)
            .limit(pageable.page_size)
            )
            if pageable.size != 0
            else select(Pizzeria).options(joinedload(Pizzeria.pizzas))
        )
        pizzerias: Final = session.scalars(statement).all()
        logger.debug("{}", pizzerias)

        statement_count: Final = select(func.count()).select_from(Pizzeria)
        total_elements: Final = session.scalar(statement_count)
        logger.debug("total_elements={}", total_elements)

        return Slice(content=pizzerias, total_elements=total_elements)

    def _find_by_email(self, email: str, session: Session) -> Pizzeria | None:
        logger.debug(f"Repository._find_by_email(email={email})")
        statement: Final = (
            select(Pizzeria)
            .where(func.lower(Pizzeria.email) == func.lower(email))
        )
        pizzeria: Final = session.scalar(statement)
        logger.debug("{}", pizzeria)
        return pizzeria
    def _find_by_name(self, teil: str, pageable: Pageable, session: Session) -> Slice[Pizzeria] | None:
        logger.debug(f"Repository._find_by_name(teil={teil}, pageable={pageable})")
        statement: Final = (
            select(Pizzeria)
            .where(func.lower(Pizzeria.name).like(f"%{teil.lower()}%"))
            .offset(pageable.offset)
            .limit(pageable.page_size)
        )
        pizzerias: Final = session.scalars(statement).all()
        logger.debug("{}", pizzerias)

        statement_count: Final = (
            select(func.count())
            .select_from(Pizzeria)
            .where(func.lower(Pizzeria.name).like(f"%{teil.lower()}%"))
        )
        total_elements: Final = session.scalar(statement_count)
        logger.debug("total_elements={}", total_elements)

        return Slice(content=pizzerias, total_elements=total_elements)
