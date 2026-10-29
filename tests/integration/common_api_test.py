# Copyright (C) 2026
#
# Integrationstests fuer das Pizzeria-Projekt.
# Orientiert an der Vorlage von Juergen Zimmermann,
# Hochschule Karlsruhe.

"""Allgemeine Daten und Hilfsfunktionen fuer die Integrationstests."""

from http import HTTPStatus
from pathlib import Path
from typing import Any, Final

from requests import get, post, request


__all__ = [
    "base_url",
    "certificate_path",
    "check_readiness",
    "db_populate",
    "db_populate_path",
    "graphql_path",
    "graphql_url",
    "health_url",
    "keycloak_populate",
    "keycloak_populate_path",
    "login",
    "login_graphql",
    "password_admin",
    "rest_path",
    "rest_url",
    "timeout",
    "token_path",
    "username_admin",
]


# -------------------------------------------------------------------
# Serverkonfiguration
# -------------------------------------------------------------------

schema: Final = "https"

port: Final = 8000

host: Final = "127.0.0.1"

base_url: Final = f"{schema}://{host}:{port}"


# -------------------------------------------------------------------
# REST-Schnittstelle
# -------------------------------------------------------------------

rest_path: Final = "/rest"

rest_url: Final = f"{base_url}{rest_path}"


# -------------------------------------------------------------------
# Health-Schnittstelle
# -------------------------------------------------------------------

health_url: Final = f"{base_url}/health"


# -------------------------------------------------------------------
# GraphQL-Schnittstelle
# -------------------------------------------------------------------

graphql_path: Final = "/graphql"

graphql_url: Final = f"{base_url}{graphql_path}"


# -------------------------------------------------------------------
# Authentifizierung
# -------------------------------------------------------------------

token_path: Final = "/auth/token"

username_admin: Final = "admin"

password_admin: Final = "p"


# -------------------------------------------------------------------
# Initialisierung der Testdaten
# -------------------------------------------------------------------

db_populate_path: Final = "/dev/db_populate"

keycloak_populate_path: Final = "/dev/keycloak_populate"


# -------------------------------------------------------------------
# HTTP-Konfiguration und TLS-Zertifikat
# -------------------------------------------------------------------

timeout: Final = 2

certificate_path: Final = str(
    Path(__file__).resolve().parents[2]
    / "src"
    / "pizzeria"
    / "config"
    / "resources"
    / "tls"
    / "certificate.crt"
)


# -------------------------------------------------------------------
# Readiness pruefen
# -------------------------------------------------------------------

def check_readiness() -> None:
    """Pruefen, ob der FastAPI-Server und die Datenbank bereit sind."""

    response: Final = get(
        f"{health_url}/readiness",
        timeout=timeout,
        verify=certificate_path,
    )

    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(
            f"readiness mit Statuscode {response.status_code}"
        )

    response_body: Final = response.json()

    if not isinstance(response_body, dict):
        raise TypeError(
            "readiness ohne Dictionary im Response-Body"
        )

    status: Final[Any | None] = response_body.get("db")

    if status != "up":
        raise RuntimeError(
            f"readiness mit Meldungstext {status}"
        )


# -------------------------------------------------------------------
# REST-Login
# -------------------------------------------------------------------

def login(
    username: str = username_admin,
    password: str = password_admin,
) -> str:
    """Login ueber REST, um einen JWT von Keycloak zu erhalten."""

    login_data: Final = {
        "username": username,
        "password": password,
    }

    response: Final = request(
        method="POST",
        url=f"{base_url}{token_path}",
        json=login_data,
        timeout=timeout,
        verify=certificate_path,
    )

    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(
            f"login() mit Statuscode {response.status_code}"
        )

    response_body: Final = response.json()

    token: Final = response_body.get("token")

    if token is None or not isinstance(token, str):
        raise RuntimeError(
            f"login() mit ungueltigem Token: type={type(token)}"
        )

    return token


# -------------------------------------------------------------------
# GraphQL-Login
# -------------------------------------------------------------------

def login_graphql(
    username: str = username_admin,
    password: str = password_admin,
) -> str:
    """Login ueber GraphQL, um einen JWT von Keycloak zu erhalten."""

    login_query: Final = {
        "query": (
            "mutation ($username: String!, $password: String!) { "
            "login(username: $username, password: $password) "
            "{ token } "
            "}"
        ),
        "variables": {
            "username": username,
            "password": password,
        },
    }

    response: Final = post(
        graphql_url,
        json=login_query,
        timeout=timeout,
        verify=certificate_path,
    )

    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(
            f"login_graphql() mit Statuscode {response.status_code}"
        )

    response_body: Final = response.json()

    data = response_body.get("data")

    if not isinstance(data, dict):
        raise RuntimeError(
            "login_graphql() ohne gueltige GraphQL-Daten"
        )

    login_result = data.get("login")

    if not isinstance(login_result, dict):
        raise RuntimeError(
            "login_graphql() ohne gueltiges Login-Ergebnis"
        )

    token: Final = login_result.get("token")

    if token is None or not isinstance(token, str):
        raise RuntimeError(
            f"login_graphql() mit ungueltigem Token: type={type(token)}"
        )

    return token


# -------------------------------------------------------------------
# Datenbank mit Testdaten initialisieren
# -------------------------------------------------------------------

def db_populate() -> None:
    """Datenbank mit den vorgesehenen Testdaten neu initialisieren."""

    token: Final = login()

    headers: Final = {
        "Authorization": f"Bearer {token}"
    }

    response: Final = request(
        method="QUERY",
        url=f"{base_url}{db_populate_path}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.OK


# -------------------------------------------------------------------
# Keycloak mit Testdaten initialisieren
# -------------------------------------------------------------------

def keycloak_populate() -> None:
    """Keycloak mit den vorgesehenen Testdaten neu initialisieren."""

    token: Final = login()

    headers: Final = {
        "Authorization": f"Bearer {token}"
    }

    response: Final = request(
        method="QUERY",
        url=f"{base_url}{keycloak_populate_path}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.OK
