"""REST-Endpunkte zum Anlegen, Aktualisieren und Loeschen von Pizzerien."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from pizzeria.problem_details import ProblemDetails
from pizzeria.router.constants import IF_MATCH, IF_MATCH_MIN_LEN
from pizzeria.router.dependencies import get_write_service
from pizzeria.router.pizzeria_model import PizzeriaModel
from pizzeria.router.pizzeria_update_model import pizzeriaUpdateModel
from pizzeria.security import Role, RolesRequired
from pizzeria.service.pizzeria_write_service import pizzeriaWriteService

__all__ = ["pizzeria_write_router"]


pizzeria_write_router: Final = APIRouter(tags=["Schreiben"])


@pizzeria_write_router.post("")
def post(
    pizzeria_model: PizzeriaModel,
    request: Request,
    service: Annotated[pizzeriaWriteService, Depends(get_write_service)],
) -> Response:
    """POST-Request, um eine neue Pizzeria anzulegen."""
    logger.debug("pizzeria_model={}", pizzeria_model)

    pizzeria_dto: Final = service.create(
        pizzeria=pizzeria_model.to_pizzeria(),
    )

    logger.debug("pizzeria_dto={}", pizzeria_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={
            "Location": f"{request.url.path.rstrip('/')}/{pizzeria_dto.id}"
        },
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
    """PUT-Request, um eine Pizzeria zu aktualisieren."""

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
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.PIZZERIA]))],
)
def delete_by_id(
    pizzeria_id: int,
    service: Annotated[pizzeriaWriteService, Depends(get_write_service)],
) -> Response:
    """DELETE-Request, um eine Pizzeria anhand ihrer ID zu löschen."""

    logger.debug("pizzeria_id={}", pizzeria_id)

    service.delete_by_id(pizzeria_id=pizzeria_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
