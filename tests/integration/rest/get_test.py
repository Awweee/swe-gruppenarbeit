"""Integrationstests für GET /rest mit Query-Parametern."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import get


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize(
    "email",
    [
        "admin@acme.com",
        "info@pizzeria-napoli.de",
    ],
)
def test_get_by_email(email: str) -> None:
    # arrange
    params = {"email": email}

    token: Final = login()
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        rest_url,
        params=params,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK

    response_body: Final = response.json()
    content: Final = response_body["content"]

    assert isinstance(content, list)
    assert len(content) == 1

    pizzeria = content[0]

    assert pizzeria is not None
    assert pizzeria.get("email") == email
    assert pizzeria.get("id") is not None


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize(
    "email",
    [
        "nicht@vorhanden.de",
        "unbekannt@example.com",
    ],
)
def test_get_by_email_not_found(email: str) -> None:
    # arrange
    params = {"email": email}

    token: Final = login()
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        rest_url,
        params=params,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND
