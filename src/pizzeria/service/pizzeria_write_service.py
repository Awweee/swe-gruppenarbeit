# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Geschäftslogik zum Schreiben von Pizzeriadaten."""

from typing import Final

from loguru import logger

from pizzeria.repository import repository, Session
from pizzeria.security import User, UserService
from pizzeria.service.exceptions import (
    EmailExistsError,
    EmptyUsernameError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
from pizzeria.service.pizzeria_dto import PizzeriaDTO
lazy from pizzeria.entity import Pizzeria

__all__ = ["pizzeriaWriteService"]


class pizzeriaWriteService:
    """Service-Klasse mit Geschäftslogik für Pizzerien."""

    def __init__(self, repo: repository, user_service: UserService) -> None:
        """Konstruktor mit abhängigem Repository und UserService."""
        self.repo: repository = repo
        self.user_service: UserService = user_service

    def create(self, pizzeria: Pizzeria) -> PizzeriaDTO:
        """Eine neue Pizzeria anlegen.

        :param pizzeria: Die neue Pizzeria ohne ID
        :return: Die neu angelegte Pizzeria mit generierter ID
        :rtype: PizzeriaDTO
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug(
            "pizzeria={}, adresse={}, pizzen={}",
            pizzeria,
            pizzeria.adresse,
            pizzeria.pizzen,
        )

        username: Final = pizzeria.username
        if username is None:
            raise EmptyUsernameError

        # https://www.keycloak.org/docs-api/latest/rest-api:
        # GET /admin/realms/{realm}/users
        if self.user_service.username_exists(username):
            raise UsernameExistsError(username)

        email: Final = pizzeria.email
        if self.user_service.email_exists(email):
            raise EmailExistsError(email=email)

        user: Final = User(
            username=username,
            email=pizzeria.email,
            nachname=pizzeria.name,
            vorname=pizzeria.name,
            password="p",  # ruff: ignore[hardcoded-password-func-arg] # NOSONAR
            roles=[],
        )
        user_id = self.user_service.create_user(user)
        logger.debug("user_id={}", user_id)

        # durch "with" erhaelt man einen "Context Manager", der die Ressource/Session
        # am Ende des Blocks schliesst
        with Session() as session:


            pizzeria_db: Final = self.repo.create(
                pizzeria=pizzeria,
                session=session,
            )
            pizzeria_dto: Final = PizzeriaDTO.from_pizzeria(pizzeria_db)
            session.commit()

        # TODO User aus Keycloak loeschen, falls die DB-Transaktion fehlschlaegt

        logger.debug("pizzeria_dto={}", pizzeria_dto)
        return pizzeria_dto

    def update(
        self,
        pizzeria: Pizzeria,
        pizzeria_id: int,
        version: int,
    ) -> PizzeriaDTO:
        """Daten einer Pizzeria ändern.

        :param pizzeria: Die neuen Daten
        :param pizzeria_id: ID der zu aktualisierenden Pizzeria
        :param version: Version für optimistische Synchronisation
        :return: Die aktualisierte Pizzeria
        :rtype: PizzeriaDTO
        :raises NotFoundError: Falls die Pizzeria nicht existiert
        :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug(
            "pizzeria_id={}, version={}, {}",
            pizzeria_id,
            version,
            pizzeria,
        )

        with Session() as session:
            if (
                pizzeria_db := self.repo.find_by_id(
                    pizzeria_id=pizzeria_id,
                    session=session,
                )
            ) is None:
                raise NotFoundError(pizzeria_id)

            if pizzeria_db.version > version:
                raise VersionOutdatedError(version)


            pizzeria_db.set(pizzeria)

            if (
                pizzeria_updated := self.repo.update(
                    pizzeria=pizzeria_db,
                    session=session,
                )
            ) is None:
                raise NotFoundError(pizzeria_id)

            pizzeria_dto: Final = PizzeriaDTO.from_pizzeria(pizzeria_updated)
            logger.debug("{}", pizzeria_dto)

            session.commit()

            # CAVEAT: Die erhoehte Versionsnummer ist erst nach COMMIT sichtbar
            pizzeria_dto.version += 1

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
