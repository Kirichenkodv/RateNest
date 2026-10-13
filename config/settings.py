from pathlib import Path
from typing import Annotated

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None)

    DJANGO_SECRET_KEY: str
    DJANGO_DEBUG: bool = False
    DJANGO_ALLOWED_HOSTS: Annotated[list[str], NoDecode] = Field(default_factory=list)

    DATABASE_URL: str
    REDIS_URL: str

    @field_validator("DJANGO_ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [host.strip() for host in value.split(",") if host.strip()]
        return value


try:
    env = Settings()
except ValidationError as exc:
    fields = sorted(
        {
            ".".join(str(part) for part in error["loc"])
            for error in exc.errors(include_input=False)
            if error.get("loc")
        }
    )
    field_names = ", ".join(fields) or "неизвестные настройки"

    raise ImproperlyConfigured(
        f"Некорректные настройки Django. Проверьте переменные: {field_names}."
    ) from None

SECRET_KEY = env.DJANGO_SECRET_KEY
DEBUG = env.DJANGO_DEBUG
ALLOWED_HOSTS = env.DJANGO_ALLOWED_HOSTS

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "dmr",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

try:
    default_database = dj_database_url.parse(env.DATABASE_URL)
except ValueError:
    raise ImproperlyConfigured(
        "Некорректная переменная DATABASE_URL. "
        "Проверьте формат URL, схему и кодирование специальных символов."
    ) from None

DATABASES = {
    "default": default_database,
}

REDIS_URL = env.REDIS_URL


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"
