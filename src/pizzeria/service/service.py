from datetime import datetime
from typing import Final
from zoneinfo import ZoneInfo
lazy from collections.abc import Sequence

from loguru import logger
from openpyxl import Workbook

from pizzeria.entity.pizzeria import Pizzeria
from pizzeria.repository import (
    Pageable,
    repository,
    Suchparameter,
    Session,
    Slice,
)
from pizzeria.security import Role, User
from pizzeria.service import pizzeria_dto
from pizzeria.service.exceptions import ForbiddenError, NotFoundError
from pizzeria.service.pizzeria_dto import PizzeriaDTO

class Service:
    """Service-Klasse für die Verwaltung von Pizzerien."""

    def __init__(self, repo:repository):
        self.repository = repo

    def find_by_id(self, pizzeria_id: int | None, user: User) -> Pizzeria | None:
         logger.debug("pizzeria_id={}, user={}", pizzeria_id, user)
         with Session() as session:
            user_is_admin: Final = Role.ADMIN in user.roles

            if (
                pizzeria := self.repository.find_by_id(session=session, pizzeria_id=pizzeria_id)
            ) is None:
                if user_is_admin:
                    message: Final = f"Keine Pizzeria mit der ID {pizzeria_id}"
                    logger.debug("NotFoundError: {}", message)
                    # "Throw Exceptions Instead of Returning Errors"
                    raise NotFoundError(pizzeria_id=pizzeria_id)
                logger.debug("nicht admin")
                raise ForbiddenError
            if pizzeria.username != user.username and not user_is_admin:
                logger.debug(
                    "pizzeria.username={}, user.username={}, user.roles={}",
                    pizzeria.username,
                    user.username,
                    user.roles,
                )
                raise ForbiddenError

            pizzeria_dto: Final = PizzeriaDTO.from_pizzeria(pizzeria)
            session.commit()

            logger.debug("{}", pizzeria_dto)
            return pizzeria_dto
    def find(
        self,
        suchparameter: Suchparameter | None,
        pageable: Pageable,
    ) -> Slice[PizzeriaDTO]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter oder None
        :return: Liste der gefundenen pizzeriaen
        :rtype: Slice[pizzeriaDTO]
        :raises NotFoundError: Falls keine pizzeriaen gefunden wurden
        """
        logger.debug("{}", suchparameter)
        with Session() as session:
            pizzeria_slice: Final = self.repository.find(
                suchparameter=suchparameter,
                pageable=pageable,
                session=session,
            )
            if len(pizzeria_slice.content) == 0:
                raise NotFoundError(suchparameter=suchparameter)

            # tuple mit einem "Generator"-Ausdruck
            # vgl. List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
            pizzerien_dto: Final = tuple(
                PizzeriaDTO.from_pizzeria(pizzeria) for pizzeria in pizzeria_slice.content
            )
            session.commit()
        pizzerien_dto_slice = Slice(
            content=pizzerien_dto,
            total_elements=pizzeria_slice.total_elements,
        )
        logger.debug("{}", pizzerien_dto_slice)
        return pizzerien_dto_slice
