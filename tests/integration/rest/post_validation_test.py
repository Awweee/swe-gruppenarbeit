"""Integrationstests für die Validierung von POST /rest."""

from copy import deepcopy
from http import HTTPStatus
from typing import Any, Final

import pytest
from common_api_test import certificate_path, rest_url, timeout
from requests import post


@pytest.mark.rest
@pytest.mark.parametrize(
    ("feld", "wert"),
    [
        ("name", ""),
        ("name", "A" * 89),
        ("adresse", None),
        ("pizzen", None),
    ],
    ids=[
        "leerer_name",
        "name_zu_lang",
        "adresse_null",
        "pizzen_null",
    ],
)
def test_post_invalid_fields(feld: str, wert: Any) -> None:
    """Ungültige Pflichtfelder liefern HTTP 422."""

    # arrange
    neue_pizzeria: dict[str, Any] = {
        "name": "Pizzeria Test",
        "telefon": "0721 123456",
        "email": "integration@example.com",
        "username": "integration-test",
        "adresse": {
            "strasse": "Teststrasse",
            "hausnummer": "10",
            "plz": "76133",
            "ort": "Karlsruhe",
        },
        "pizzen": [],
    }

    neue_pizzeria[feld] = wert

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

    assert "detail" in response_body


@pytest.mark.rest
@pytest.mark.parametrize(
    ("feld", "wert"),
    [
        ("plz", "123"),
        ("ort", ""),
    ],
    ids=[
        "ungueltige_plz",
        "leerer_ort",
    ],
)
def test_post_invalid_address(feld: str, wert: str) -> None:
    """Ungültige Adressdaten liefern HTTP 422."""

    # arrange
    neue_pizzeria: dict[str, Any] = {
        "name": "Pizzeria Test",
        "telefon": "0721 123456",
        "email": "integration@example.com",
        "username": "integration-test",
        "adresse": {
            "strasse": "Teststrasse",
            "hausnummer": "10",
            "plz": "76133",
            "ort": "Karlsruhe",
        },
        "pizzen": [],
    }

    neue_pizzeria = deepcopy(neue_pizzeria)

    neue_pizzeria["adresse"][feld] = wert

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

    assert "detail" in response_body
