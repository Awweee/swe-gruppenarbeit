# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Schema für GraphQL durch Strawberry.

Alternative: https://github.com/graphql-python/graphene.
"""

from dataclasses import asdict
from typing import Final
lazy from collections.abc import Sequence

import strawberry
from fastapi import Request
from loguru import logger
from strawberry.extensions import PydanticErrorExtension
from strawberry.fastapi import GraphQLRouter
lazy from strawberry.types import Info

from pizzeria.config.graphql import graphql_ide
from pizzeria.graphql_api.graphql_types import (
    CreatePayload,
    LoginResult,
    PizzeriaInput,
    Suchparameter,
)
from pizzeria.repository import Pageable, repository, suchparameter
from pizzeria.router.pizzeria_model import PizzeriaModel
from pizzeria.security import Role, TokenService, UserService
from pizzeria.service import (
    NotFoundError,
    PizzeriaDTO,
    Service,
)
from pizzeria.service.pizzeria_write_service import pizzeriaWriteService

#from pizzeria.service import pizzeriaWriteService

__all__ = ["graphql_router"]


# Strawberry ist eine "code-first library":
# - keine Schema-Datei in SDL (schema definition language) notwendig
# - das Schema wird aus Klassen generiert, die mit z.B. @type oder @input dekoriert sind

# type pizzeria {
#     nachname: String!
# }
# input Suchparameter {...}
# type Query {
#     pizzeria(pizzeria_id: ID!): pizzeria!
#     pizzeriaen(suchparameter: Suchparameter): list[pizzeria!]!
# }


_repo: Final = repository()
_service: Service = Service(repo=_repo)
_user_service: UserService = UserService()
_write_service: pizzeriaWriteService = pizzeriaWriteService(
     repo=_repo,
     user_service=_user_service,
 )
_token_service: Final = TokenService()


@strawberry.type  # vgl. @dataclass
class Query:
    """Queries, um pizzeriaendaten zu lesen."""

    @strawberry.field
    def pizzeria(self, pizzeria_id: strawberry.ID, info: Info) -> PizzeriaDTO | None:
        """Daten zu einem pizzeriaen lesen.

        :param pizzeria_id: ID des gesuchten pizzeriaen
        :return: Gesuchter pizzeria
        :rtype: pizzeria
        :raises NotFoundError: Falls kein pizzeria gefunden wurde, wird zu GraphQLError
        """
        logger.debug("pizzeria_id={}", pizzeria_id)

        request: Final[Request] = info.context.get("request")
        user: Final = _token_service.get_user_from_request(request=request)
        if user is None:
            return None

        try:
            pizzeria_dto: Final = _service.find_by_id(
                pizzeria_id=int(pizzeria_id),
                user=user,
            )
        except NotFoundError:
            return None
        logger.debug("{}", pizzeria_dto)
        return pizzeria_dto

    @strawberry.field
    def pizzeriaen(
        self,
        suchparameter: Suchparameter | None,
        info: Info,
    ) -> Sequence[PizzeriaDTO]:
        """pizzeriaen anhand von Suchparameter suchen.

        :param suchparameter: nachname, email usw.
        :return: Die gefundenen pizzeriaen
        :rtype: list[pizzeria]
        :raises NotFoundError: Falls kein pizzeria gefunden wurde, wird zu GraphQLError
        """
        logger.debug("suchparameter={}", suchparameter)

        request: Final[Request] = info.context["request"]
        user: Final = _token_service.get_user_from_request(request)
        if user is None or Role.ADMIN not in user.roles:
            return []

        suchparameter_filtered = (
            None
            if suchparameter is None
            else suchparameter(
                email=suchparameter.email,
                nachname=suchparameter.nachname,
            )
        )
        logger.debug("suchparameter_filtered={}", suchparameter_filtered)

        pageable: Final = Pageable.create(size=str(0))
        try:
            pizzeriaen_dto: Final = _service.find(
                suchparameter=suchparameter_filtered,
                pageable=pageable,
            )
        except NotFoundError:
            return []
        logger.debug("{}", pizzeriaen_dto)
        return pizzeriaen_dto.content


@strawberry.type
class Mutation:
    """Mutations, um pizzeriaendaten anzulegen, zu ändern oder zu löschen."""

    @strawberry.mutation
    def create(self, pizzeria_input: PizzeriaInput) -> CreatePayload:
        """Einen neuen pizzeriaen anlegen.

        :param pizzeria_input: Daten des neuen pizzeriaen
        :return: ID des neuen pizzeriaen
        :rtype: CreatePayload
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        :raises UsernameExistsError: Falls der Benutzername bereits existiert
        """
        logger.debug("pizzeria_input={}", pizzeria_input)

        # Dictonary mit Pydantic validieren
        pizzeria_model: Final = PizzeriaModel.model_validate(asdict(pizzeria_input))

        pizzeria_dto: Final = _write_service.create(pizzeria=pizzeria_model.to_pizzeria())
        payload: Final = CreatePayload(id=pizzeria_dto.id)

        logger.debug("{}", payload)
        return payload

    # Mutation, weil evtl. der Login-Zeitpunkt gespeichert wird
    @strawberry.mutation
    def login(self, username: str, password: str) -> LoginResult:
        """Einen Token zu Benutzername und Passwort ermitteln.

        :param username: Benutzername
        :param password: Passwort
        :rtype: LoginResult
        """
        logger.debug("username={}, password={}", username, password)
        token_mapping = _token_service.token(username=username, password=password)

        token = token_mapping["access_token"]
        user = _token_service.get_user_from_token(token)
        # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
        roles: Final = [role.value for role in user.roles]
        return LoginResult(token=token, expiresIn="1d", roles=roles)


schema: Final = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    # https://strawberry.rocks/docs/extensions/pydantic_error_extension
    extensions=[
        PydanticErrorExtension,
    ],
)


Context = dict[str, Request]


# Dependency Injection: Request von FastAPI weiterreichen an den Kontext von Strawberry
def get_context(request: Request) -> Context:
    return {"request": request}


# https://strawberry.rocks/docs/integrations/fastapi
graphql_router: Final = GraphQLRouter[Context](
    schema,
    context_getter=get_context,
    graphql_ide=graphql_ide,
)
