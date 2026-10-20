from typing import Annotated, Final

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from pizzeria.router.constants import ETAG, IF_NONE_MATCH, IF_NONE_MATCH_MIN_LEN
from pizzeria.router.dependencies import get_service
from pizzeria.router.pizzeria_find_model import (
    pizzeriaFindModel,
    pizzeriaPageModel,
    pizzeriaResponseModel,
)
from pizzeria.security import Role, RolesRequired, User
lazy from pizzeria.service import service

pizzeria_router: Final = APIRouter(tags=["Lesen"])

@pizzeria_router.get(
    path="/{pizzeria_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.PIZZERIA]))],
    response_model=pizzeriaResponseModel,
)
def get_by_id(
    pizzeria_id: int,
    request: Request,
    service: Annotated[service, Depends(get_service)],
) -> Response:
    """Suche mit der pizzeria-ID.

    :param pizzeria_id: ID des gesuchten pizzeriaen als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit ggf. If-None-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit dem gefundenen pizzeriaendatensatz
    :rtype: Response
    :raises NotFoundError: Falls kein pizzeria gefunden wurde
    :raises ForbiddenError: Falls die pizzeriaendaten nicht gelesen werden dürfen
    """
    # User-Objekt ist durch Depends(RolesRequired()) in Request.state gepuffert
    user: Final[User] = request.state.current_user
    logger.debug("pizzeria_id={}, user={}", pizzeria_id, user)

    pizzeria: Final = service.find_by_id(pizzeria_id=pizzeria_id, user=user)
    logger.debug("{}", pizzeria)

    if_none_match: Final = request.headers.get(IF_NONE_MATCH)
    if (
        if_none_match is not None
        and len(if_none_match) >= IF_NONE_MATCH_MIN_LEN
        and if_none_match.startswith('"')
        and if_none_match.endswith('"')
    ):
        version = if_none_match[1:-1]
        logger.debug("version={}", version)
        if version is not None:
            try:
                if int(version) == pizzeria.version:
                    return Response(status_code=status.HTTP_304_NOT_MODIFIED)
            except ValueError:
                logger.debug("invalid version={}", version)

    pizzeria_model: Final = pizzeriaResponseModel.from_dto(pizzeria)
    return JSONResponse(
        content=pizzeria_model.model_dump(mode="json"),
        headers={ETAG: f'"{pizzeria.version}"'},
    )
