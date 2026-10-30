# Copyright (C) 2025 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Factory-Funktionen für Dependency Injection."""

from typing import Annotated

from fastapi import Depends

from pizzeria.repository.repository import repository
from pizzeria.security.dependencies import get_user_service
from pizzeria.service.pizzeria_write_service import pizzeriaWriteService
from pizzeria.service.service import Service
lazy from pizzeria.security.user_service import UserService


def get_repository() -> repository:
    """Factory-Funktion für repository.

    :return: Das Repository
    :rtype: repository
    """
    return repository()


def get_service(
    repo: Annotated[repository, Depends(get_repository)],
) -> Service:
    """Factory-Funktion für service."""
    return Service(repo=repo)


def get_write_service(
    repo: Annotated[repository, Depends(get_repository)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> pizzeriaWriteService:
    """Factory-Funktion für pizzeriaWriteService."""
    return pizzeriaWriteService(repo=repo, user_service=user_service)
