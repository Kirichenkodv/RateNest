"""GET /api/health/ — проверка базы и Redis."""

import time

import pytest
from django.test import Client
from pytest_django.fixtures import Settings

URL = "/api/health/"
CLOSED_REDIS_URL = "redis://localhost:1/0"

pytestmark = pytest.mark.django_db


def test_health_ok(client: Client) -> None:
    response = client.get(URL)

    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/json")
    assert response.json() == {
        "status": "ok",
        "checks": {"database": "ok", "redis": "ok"},
    }


def test_health_redis_unavailable(client: Client, settings: Settings) -> None:
    settings.REDIS_URL = CLOSED_REDIS_URL

    response = client.get(URL)

    assert response.status_code == 503
    assert response.json() == {
        "status": "error",
        "checks": {"database": "ok", "redis": "error"},
    }


def test_health_redis_unavailable_responds_fast(client: Client, settings: Settings) -> None:
    settings.REDIS_URL = CLOSED_REDIS_URL

    started = time.monotonic()
    client.get(URL)

    assert time.monotonic() - started < 3


def test_health_only_get_allowed(client: Client) -> None:
    assert client.post(URL).status_code == 405


def test_health_in_openapi_schema(client: Client) -> None:
    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    responses = response.json()["paths"]["/api/health/"]["get"]["responses"]
    assert {"200", "503"} <= set(responses)
