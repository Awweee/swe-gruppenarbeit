"""Integrationstests für GET /rest/{pizzeria_id}."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import get


@pytest.mark.rest
@pytest.mark.get_request
def test_get_by_id() -> None:
    """Vorhandene Pizzeria anhand ihrer ID abrufen."""

    # arrange
    pizzeria_id: Final = 1

    token: Final = login()

    headers: Final = {
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = get(
        f"{rest_url}/{pizzeria_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK

    response_body: Final = response.json()

    assert response_body is not None
    assert response_body["id"] == pizzeria_id
    assert response_body["name"] == "Admin"
    assert response_body["email"] == "admin@acme.com"


@pytest.mark.rest
@pytest.mark.get_request
def test_get_by_id_not_found() -> None:
    """Nicht vorhandene Pizzeria liefert HTTP 404."""

    # arrange
    pizzeria_id: Final = 999999

    token: Final = login()

    headers: Final = {
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = get(
        f"{rest_url}/{pizzeria_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.rest
@pytest.mark.get_request
def test_get_by_id_unauthorized() -> None:
    """Anfrage ohne JWT-Token liefert HTTP 401."""

    # arrange
    pizzeria_id: Final = 1

    # act
    response: Final = get(
        f"{rest_url}/{pizzeria_id}",
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED
