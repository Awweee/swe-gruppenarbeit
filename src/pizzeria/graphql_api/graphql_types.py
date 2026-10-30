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

"""Schema für GraphQL."""

lazy from datetime import date
lazy from decimal import Decimal

import strawberry

lazy from pizzeria.entity import (
    Adresse,
    Pizza,
    Pizzeria,
)

__all__ = [
    "AdresseInput",
    "CreatePayload",
    "PizzeriaInput",
    "RechnungInput",
    "Suchparameter",
    "PizzaInput",
]

# SDL (schema definition language):
# type pizzeria {
#     nachname: String!
# }
# type Query {
#     pizzeria(pizzeria_id: ID!): pizzeria!
#     pizzeriaen(input: Suchparameter): [pizzeria!]
# }
# type Mutation {
#     create(pizzeria_input: pizzeriaInput!): CreatePayload!
# }
@strawberry.input
class Suchparameter:
    """Suchparameter für die Suche nach pizzeriaen."""

    nachname: str | None = None
    """Nachname als Suchkriterium."""

    email: str | None = None
    """Emailadresse als Suchkriterium."""

@strawberry.input
class PizzaInput:
    """Daten für eine neue Pizza."""

    name: str
    """Name der Pizza."""

    beschreibung: str | None = None
    """Beschreibung der Pizza."""

    preis: Decimal
    """Preis der Pizza."""

    vegetarisch: bool
    """Gibt an, ob die Pizza vegetarisch ist."""

@strawberry.input
class AdresseInput:
    """Adresse eines neuen pizzeriaen."""

    plz: str
    """Postleitzahl eines neuen pizzeriaen."""

    ort: str
    """Ort eines neuen pizzeriaen."""


@strawberry.input
class RechnungInput:
    """Rechnung zu einem neuen pizzeriaen."""

    betrag: Decimal
    """Betrag."""

    waehrung: str
    """Währung als 3-stellige Zeichenkette."""


@strawberry.input
class PizzeriaInput:
    """Daten für einen neuen pizzeriaen."""

    name: str
    """Name."""

    email: str
    """Emailadresse."""

    adresse: AdresseInput
    """Adresse."""

    telefon: str | None = None
    """Telefonnummer."""

    pizzen: list[PizzaInput] | None = None


@strawberry.type
class CreatePayload:
    """Resultat-Typ, wenn ein neuer pizzeria angelegt wurde."""

    id: int
    """ID des neu angelegten pizzeriaen"""


@strawberry.type
class LoginResult:
    """Resultat-Typ, wenn ein Login erfolgreich war."""

    token: str
    """Token des eingeloggten Users."""
    expiresIn: str  # ruff: ignore[mixed-case-variable-in-class-scope]  # NOSONAR
    """Gültigkeitsdauer des Tokens."""
    roles: list[str]
    """Rollen des eingeloggten Users."""

