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
@pizzeria_router.get(
    path="",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
    response_model=pizzeriaPageModel,
    )
def get(
        find_model: Annotated[pizzeriaFindModel, Query()],
        service: Annotated[service, Depends(get_service)],
    ) -> pizzeriaPageModel:
        """Suche mit Query-Parameter.

        Siehe https://fastapi.tiangolo.com/tutorial/query-params und
        https://fastapi.tiangolo.com/de/tutorial/query-param-models
        :param find_model: Validierte Such- und Pagination-Parameter als Pydantic-Model
        :param service: Injizierter Service für Geschäftslogik
        :return: Eine Seite mit pizzeriaen-Daten
        :raises NotFoundError: Falls keine pizzeriaen gefunden wurden
        """
        logger.debug("search={}", find_model)
        result: Final = _find_page(service=service, find_model=find_model)
        logger.debug("result={}", result)
        return result

@pizzeria_router.api_route(
    path="/query",
    methods=["QUERY"],
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
    response_model=pizzeriaPageModel,
)
def query(
    find_model: pizzeriaFindModel,
    service: Annotated[service, Depends(get_service)],
) -> pizzeriaPageModel:
    """Suche mit HTTP-Methode _QUERY_.

    **BEACHTE**: HTTP-Methode QUERY ist in FastAPI noch nicht "nativ" implementiert
    https://github.com/fastapi/fastapi/issues/12965 und
    https://www.rfc-editor.org/info/rfc10008
    :param find_model: Validierte Suchparameter (einschließlich Pagination) als
    Pydantic-Model aus dem Request-Body
    :param service: Injizierter Service für Geschäftslogik
    :return: Eine Seite mit pizzeriaen-Daten
    :raises NotFoundError: Falls keine pizzeriaen gefunden wurden
    """
    logger.debug("search={}", find_model)
    result: Final = _find_page(service=service, find_model=find_model)
    logger.debug("result={}", result)
    return result

def _find_page(
    service: service.Service,
    find_model: pizzeriaFindModel,
) -> pizzeriaPageModel:
    pageable: Final = find_model.to_pageable()
    pizzeria_slice: Final = service.find(
        suchparameter=find_model.to_suchparameter(),
        pageable=pageable,
    )

    pizzeria_models: Final = tuple(
        pizzeriaResponseModel.from_dto(pizzeria) for pizzeria in pizzeria_slice.content
    )

    total_pages: Final = (
        (pizzeria_slice.total_elements + pageable.size - 1) // pageable.size
        if pageable.size > 0
        else 1
    )

    return pizzeriaPageModel(
        content=pizzeria_models,
        page={
            "size": pageable.size,
            "number": pageable.number,
            "total_elements": pizzeria_slice.total_elements,
            "total_pages": total_pages,
        },
    )

