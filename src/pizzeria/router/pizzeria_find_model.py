
from typing import Annotated
lazy from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from pizzeria.entity.pizza import Pizza
from pizzeria.repository import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    Pageable,
    suchparameter,
)
from pizzeria.router.pizza_model import PizzaModel
lazy from pizzeria.service import pizzeriaDTO

__all__ = ["pizzeriaFindModel", "pizzeriaPageModel", "pizzeriaResponseModel"]


class pizzeriaFindModel(BaseModel):
    """Suchparameter und Pagination für die pizzeriaensuche."""

    email: str | None = None
    nachname: str | None = None
    page: Annotated[int, Field(ge=DEFAULT_PAGE_NUMBER)] = DEFAULT_PAGE_NUMBER
    size: Annotated[int, Field(ge=0, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE

    # Keine weiteren Attribute erlaubt
    # unveraenderlich
    # https://pydantic.dev/docs/validation/latest/concepts/config
    # https://pydantic.dev/docs/validation/latest/api/pydantic/config
    model_config = ConfigDict(extra="forbid", frozen=True)

    def to_pageable(self) -> Pageable:
        """Erzeugt die Pagination-Daten aus den validierten Parametern."""
        return Pageable(number=self.page, size=self.size)

    def to_suchparameter(self) -> suchparameter:
        """Erzeugt Suchparameter für den Service."""
        return suchparameter(email=self.email, nachname=self.nachname)


class AdresseResponseModel(BaseModel):
    """Adresse als Teil eines Model-Objekts für pizzeriaen als Response.

    Damit beim Konvertieren von `pizzeriaDTO` in `pizzeriaResponseModel` auch die
    Attribute von `AdresseDTO`übernommen werden, ist `ConfigDict(from_attributes=True)`
    notwendig. Siehe
    https://pydantic.dev/docs/validation/latest/concepts/models/#nested-attributes
    """

    plz: str
    ort: str

    model_config = ConfigDict(from_attributes=True, strict=True, extra="forbid")


class pizzeriaResponseModel(BaseModel):
    """Pydantic-Modell für einen gefundenen pizzeriaen.

    FastAPI konvertiert implizit das die Felder in JSON, z.B.
    date als String "2000-01-31" oder Enum CHIRURGIE in "C".
    """

    id: int
    name: str
    telefon: str
    email: str
    adresse: str
    pizzen: list[PizzaModel]

    model_config = ConfigDict(from_attributes=True, strict=True, extra="forbid")
    # https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict

    @classmethod
    def from_dto(cls, pizzeria: pizzeriaDTO) -> pizzeriaResponseModel:
        """Konvertiert ein pizzeriaDTO in ein Pydantic-Modell für einen Response.

        Der Aufruf von `model_validate` erfordert die Übernahme der korrespondierende
        Attributwerte aus dem DTO-Objekt. Dafür ist `ConfigDict(from_attributes=True)`
        notwendig.
        Siehe https://pydantic.dev/docs/validation/latest/concepts/models/#arbitrary-class-instances
        Der Aufwand für (unnötige) Validierung ist dabei minimal:
        https://pydantic.dev/docs/validation/latest/concepts/models/#creating-models-without-validation
        """
        return cls.model_validate(pizzeria)


class PageMetaModel(BaseModel):
    """Metadaten für eine Page mit pizzeriaendaten."""

    size: int
    number: int
    total_elements: int
    total_pages: int


class pizzeriaPageModel(BaseModel):
    """Pydantic-Modell für einen Response bei einer Suche mit Pagination."""

    content: tuple[pizzeriaResponseModel, ...]
    page: PageMetaModel