"""Integrationstests für die Authentifizierung bei GET /rest."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import get


@pytest.mark.rest
@pytest.mark.get_request
def test_get_without_token() -> None:
    """GET /rest ohne JWT-Token liefert HTTP 401."""

    # arrange
    headers: Final = {}

    # act
    response: Final = get(
        rest_url,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.rest
@pytest.mark.get_request
def test_get_with_valid_token() -> None:
    """GET /rest mit gültigem JWT-Token liefert HTTP 200."""

    # arrange
    token: Final = login()

    assert token is not None

    headers: Final = {
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = get(
        rest_url,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK

    response_body: Final = response.json()

    assert "content" in response_body
    assert isinstance(response_body["content"], list)


@pytest.mark.rest
@pytest.mark.get_request
def test_get_with_invalid_token() -> None:
    """GET /rest mit ungültigem JWT-Token liefert HTTP 401."""

    # arrange
    headers: Final = {
        "Authorization": "Bearer invalid-token-12345",
    }

    # act
    response: Final = get(
        rest_url,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED
