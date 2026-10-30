"""Integrationstests für POST /rest."""

from http import HTTPStatus
from typing import Any, Final
from uuid import uuid4

import pytest
from common_api_test import certificate_path, rest_url, timeout
from requests import post


@pytest.mark.rest
def test_post_invalid() -> None:
    """Ungültige Pizzeriadaten liefern HTTP 422."""

    # arrange
    neue_pizzeria: Final[dict[str, Any]] = {
        "name": "",
        "telefon": "0721 123456",
        "email": "test@example.com",
        "username": "test-pizzeria",
        "adresse": {
            "strasse": "Teststraße",
            "hausnummer": "12",
            "plz": "76133",
            "ort": "Karlsruhe",
        },
        "pizzen": [],
    }

    # act
    response: Final = post(
        rest_url,
        json=neue_pizzeria,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    response_body: Final = response.json()

    assert response_body is not None


@pytest.mark.rest
def test_post() -> None:
    """Neue Pizzeria erfolgreich anlegen."""

    # arrange
    unique_id: Final = uuid4().hex[:12]

    neue_pizzeria: Final[dict[str, Any]] = {
        "name": "Pizzeria Integrationstest",
        "telefon": "0721 123456",
        "email": f"test-{unique_id}@example.com",
        "username": f"test-{unique_id}",
        "adresse": {
            "strasse": "Teststrasse",
            "hausnummer": "10",
            "plz": "76133",
            "ort": "Karlsruhe",
        },
        "pizzen": [],
    }

    # act
    response: Final = post(
        rest_url,
        json=neue_pizzeria,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.CREATED

    location: Final = response.headers.get("Location")

    assert location is not None
    assert location.startswith("/rest/")

    pizzeria_id: Final = int(location.rsplit("/", 1)[-1])

    assert pizzeria_id > 0
