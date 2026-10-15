"""PizzeriaWriteRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from loguru import logger

from pizzeria.router.dependencies import get_write_service
from pizzeria.router.pizzeria_model import PizzeriaModel
from pizzeria.service import PizzeriaWriteService

__all__ = ["pizzeria_write_router"]


pizzeria_write_router: Final = APIRouter(tags=["Schreiben"])


@pizzeria_write_router.post("")
def post(
    pizzeria_model: PizzeriaModel,
    request: Request,
    service: Annotated[PizzeriaWriteService, Depends(get_write_service)],
) -> Response:
    """POST-Request, um eine neue Pizzeria anzulegen.

    :param pizzeria_model: Pizzeriadaten als Pydantic-Model
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit der Request-URL
    :param service: Injizierter Service für Geschäftslogik
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    """
    logger.debug("pizzeria_model={}", pizzeria_model)

    pizzeria_dto: Final = service.create(
        pizzeria=pizzeria_model.to_pizzeria(),
    )
    logger.debug("pizzeria_dto={}", pizzeria_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{pizzeria_dto.id}"},
    )


@pizzeria_write_router.delete("/{pizzeria_id}")
def delete_by_id(
    pizzeria_id: int,
    service: Annotated[PizzeriaWriteService, Depends(get_write_service)],
) -> Response:
    """DELETE-Request, um eine Pizzeria anhand ihrer ID zu löschen.

    :param pizzeria_id: ID der zu löschenden Pizzeria
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    """
    logger.debug("pizzeria_id={}", pizzeria_id)

    service.delete_by_id(pizzeria_id=pizzeria_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
