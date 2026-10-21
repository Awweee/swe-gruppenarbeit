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

"""pizzeriaWriteRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status
from loguru import logger

from pizzeria.problem_details import ProblemDetails
from pizzeria.router.constants import IF_MATCH, IF_MATCH_MIN_LEN
from pizzeria.router.dependencies import get_write_service
from pizzeria.security import Role, RolesRequired
from pizzeria.service import send_mail
lazy from pizzeria.router.pizzeria_model import pizzeriaModel
lazy from pizzeria.router.pizzeria_update_model import pizzeriaUpdateModel
lazy from pizzeria.service import pizzeriaWriteService

__all__ = ["pizzeria_write_router"]


pizzeria_write_router: Final = APIRouter(tags=["Schreiben"])


@pizzeria_write_router.post("")
def post(
    pizzeria_model: pizzeriaModel,
    request: Request,
    background_tasks: BackgroundTasks,
    service: Annotated[pizzeriaWriteService, Depends(get_write_service)],
) -> Response:
    """POST-Request, um einen neuen pizzeriaen anzulegen.

    :param pizzeria_model: pizzeriaendaten als Pydantic-Model
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit der Request-URL
    :param background_tasks: Hintergrundtask für den Mailversand
    :param service: Injizierter Service für Geschäftslogik
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die Emailadresse bereits existiert
    :raises UsernameExistsError: Falls der Benutzername bereits existiert
    """
    logger.debug("pizzeria_model={}", pizzeria_model)
    pizzeria_dto: Final = service.create(
        pizzeria=pizzeria_model.to_pizzeria(),
    )
    logger.debug("pizzeria_dto={}", pizzeria_dto)

    background_tasks.add_task(send_mail, pizzeria_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{pizzeria_dto.id}"},
        background=background_tasks,
    )


@pizzeria_write_router.put(
    "/{pizzeria_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.PIZZERIA]))],
)
def put(
    pizzeria_id: int,
    pizzeria_update_model: pizzeriaUpdateModel,
    request: Request,
    service: Annotated[pizzeriaWriteService, Depends(get_write_service)],
) -> Response:
    """PUT-Request, um einen pizzeriaen zu aktualisieren.

    :param pizzeria_id: ID des zu aktualisierenden pizzeriaen als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit If-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die neue Emailadresse bereits
    :raises NotFoundError: Falls zur id kein pizzeria existiert
    :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
    """
    if_match_value: Final = request.headers.get(IF_MATCH)
    logger.debug(
        "pizzeria_id={}, if_match={}, pizzeria_update_model={}",
        pizzeria_id,
        if_match_value,
        pizzeria_update_model,
    )

    if if_match_value is None:
        return ProblemDetails.create(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
        ).to_response()

    if (
        len(if_match_value) < IF_MATCH_MIN_LEN
        or not if_match_value.startswith('"')
        or not if_match_value.endswith('"')
    ):
        return ProblemDetails.create(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        ).to_response()

    version: Final = if_match_value[1:-1]
    try:
        version_int: Final = int(version)
    except ValueError:
        return Response(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        )

    pizzeria: Final = pizzeria_update_model.to_pizzeria()
    pizzeria_modified: Final = service.update(
        pizzeria=pizzeria,
        pizzeria_id=pizzeria_id,
        version=version_int,
    )
    logger.debug("pizzeria_modified={}", pizzeria_modified)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": f'"{pizzeria_modified.version}"'},
    )


@pizzeria_write_router.delete(
    "/{pizzeria_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.pizzeria]))],
)
def delete_by_id(
    pizzeria_id: int,
    service: Annotated[pizzeriaWriteService, Depends(get_write_service)],
) -> Response:
    """DELETE-Request, um einen pizzeriaen anhand seiner ID zu löschen.

    :param pizzeria_id: ID des zu löschenden pizzeriaen
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    """
    logger.debug("pizzeria_id={}", pizzeria_id)
    service.delete_by_id(pizzeria_id=pizzeria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
