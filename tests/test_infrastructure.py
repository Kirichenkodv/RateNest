"""Тесты работают с настоящими PostgreSQL и Redis из docker compose / CI."""

import pytest
import redis
from django.conf import settings
from django.db import connection


@pytest.mark.django_db
def test_database_is_postgresql() -> None:
    assert connection.vendor == "postgresql"

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)


def test_redis_is_available() -> None:
    client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
    try:
        assert client.ping() is True
    finally:
        client.close()
