"""Настройки проекта читаются из переменных окружения.

Каждый тест запускает Django в отдельном процессе с явно заданным окружением,
поэтому результат не зависит от .env и переменных в твоём терминале.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

BASE_ENV = {
    "DJANGO_SECRET_KEY": "test-secret-key",
    "DATABASE_URL": "postgres://ratenest_user:s3cret@db-host:5433/ratenest_db",
    "REDIS_URL": "redis://redis-host:6379/1",
}


def run_python(code: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    clean_env = {
        "PATH": os.environ["PATH"],
        "PYTHONPATH": str(ROOT),
        "DJANGO_SETTINGS_MODULE": "config.settings",
        **env,
    }
    return subprocess.run(  # noqa: S603 — запускаем свой же интерпретатор с фиксированным кодом
        [sys.executable, "-c", code],
        env=clean_env,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def load_settings(env: dict[str, str], *names: str) -> dict[str, Any]:
    code = (
        "import json, django\n"
        "from django.conf import settings\n"
        "django.setup()\n"
        f"print(json.dumps({{n: getattr(settings, n) for n in {list(names)!r}}}, default=str))\n"
    )
    result = run_python(code, env)
    assert result.returncode == 0, result.stderr
    loaded: dict[str, Any] = json.loads(result.stdout.strip().splitlines()[-1])
    return loaded


def test_secret_key_is_required() -> None:
    env = {k: v for k, v in BASE_ENV.items() if k != "DJANGO_SECRET_KEY"}

    result = run_python("import django; django.setup()", env)

    assert result.returncode != 0
    assert "DJANGO_SECRET_KEY" in result.stderr


def test_secret_key_from_env() -> None:
    assert load_settings(BASE_ENV, "SECRET_KEY") == {"SECRET_KEY": "test-secret-key"}


def test_debug_is_off_by_default() -> None:
    assert load_settings(BASE_ENV, "DEBUG") == {"DEBUG": False}


def test_debug_can_be_enabled() -> None:
    env = {**BASE_ENV, "DJANGO_DEBUG": "true"}
    assert load_settings(env, "DEBUG") == {"DEBUG": True}


def test_debug_false_string_disables_debug() -> None:
    env = {**BASE_ENV, "DJANGO_DEBUG": "false"}
    assert load_settings(env, "DEBUG") == {"DEBUG": False}


def test_allowed_hosts_from_env() -> None:
    env = {**BASE_ENV, "DJANGO_ALLOWED_HOSTS": "example.com,api.example.com"}
    assert load_settings(env, "ALLOWED_HOSTS") == {
        "ALLOWED_HOSTS": ["example.com", "api.example.com"],
    }


def test_database_from_url() -> None:
    db = load_settings(BASE_ENV, "DATABASES")["DATABASES"]["default"]

    assert db["ENGINE"] == "django.db.backends.postgresql"
    assert db["NAME"] == "ratenest_db"
    assert db["USER"] == "ratenest_user"
    assert db["PASSWORD"] == "s3cret"
    assert db["HOST"] == "db-host"
    assert str(db["PORT"]) == "5433"


def test_redis_url_from_env() -> None:
    assert load_settings(BASE_ENV, "REDIS_URL") == {"REDIS_URL": "redis://redis-host:6379/1"}


def test_locale() -> None:
    assert load_settings(BASE_ENV, "LANGUAGE_CODE", "TIME_ZONE", "USE_TZ") == {
        "LANGUAGE_CODE": "ru",
        "TIME_ZONE": "Europe/Moscow",
        "USE_TZ": True,
    }


def test_dmr_is_installed() -> None:
    assert "dmr" in load_settings(BASE_ENV, "INSTALLED_APPS")["INSTALLED_APPS"]


def test_django_check_passes() -> None:
    result = run_python(
        "from django.core.management import execute_from_command_line; "
        "execute_from_command_line(['manage.py', 'check'])",
        BASE_ENV,
    )
    assert result.returncode == 0, result.stderr
    assert (ROOT / "manage.py").exists()
