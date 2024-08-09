"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import datetime
from enum import StrEnum
from pathlib import Path
import sys
from warnings import filterwarnings

from django.utils import timezone
from environs import Env
from loguru import logger
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


## Environment


class DeployEnvironment(StrEnum):
    PRODUCTION = "production"
    LOCAL = "local"
    TEST = "test"


DEPLOY_ENVIRONMENT = env.enum(
    "DEPLOY_ENVIRONMENT", DeployEnvironment.LOCAL, type=DeployEnvironment, ignore_case=True
)

# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

## Security

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
if DEPLOY_ENVIRONMENT != DeployEnvironment.TEST:
    DEBUG = env.bool("DEBUG", default=False)
else:
    DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", [])

if RENDER_EXTERNAL_HOSTNAME := env("RENDER_EXTERNAL_HOSTNAME", ""):
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INTERNAL_IPS = env.list("INTERNAL_IPS", [])

# TODO MAKE SURE THIS IS FINE
X_FRAME_OPTIONS = "SAMEORIGIN"

## Site

SITE_ID = 1

SITE_DOMAIN = env("SITE_DOMAIN", "www.adventhunt.com")

ROBOTS_DISALLOW_ALL = env.bool("ROBOTS_DISALLOW_ALL", default=False)

## Django App Settings

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # WhiteNoise - should be before staticfiles
    "whitenoise.runserver_nostatic",
    #
    "django.contrib.staticfiles",
    # Optional
    "django.contrib.sites",
    "django.contrib.sitemaps",
    # Third-party apps
    "allauth",
    "allauth.account",
    "crispy_forms",
    "crispy_bulma",
    "debug_toolbar",
    "robots",
    # Local apps
    "huntsite",
    "huntsite.content",
    "huntsite.puzzles",
    "huntsite.teams",
    "huntsite.tester_utils",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise - should be directly after SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",
    #
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Third-party middleware
    "allauth.account.middleware.AccountMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # Custom middleware
    "huntsite.logging.logging_middleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # allauth
                "django.template.context_processors.request",
                # Local custom context processors
                "huntsite.context_processors.meta",
                "huntsite.context_processors.canonical",
                "huntsite.context_processors.santa_missing",
                "huntsite.tester_utils.context_processors.time_travel",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


## Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "huntsite.logging.InterceptHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env("DJANGO_LOG_LEVEL", "INFO"),
        },
        "django.request": {
            "handlers": ["console"],
            "level": env("DJANGO_REQUEST_LOG_LEVEL", "WARNING"),
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": env("DJANGO_SERVER_LOG_LEVEL", "WARNING"),
            "propagate": False,
        },
    },
}

# Loguru settings

LOCAL_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "| <level>{level: <8}</level> "
    "| <yellow>{extra[request_id]}</yellow> "
    "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
    "- <level>{message}</level>"
)
PRODUCTION_FORMAT = "{extra[request_id]} | {name}:{function}:{line} - {message}"

logger.configure(extra={"request_id": "N/A"})

logger.remove(0)
if DEPLOY_ENVIRONMENT == DeployEnvironment.LOCAL:
    # Console logger
    logger.add(sys.stderr, format=LOCAL_FORMAT, backtrace=True, diagnose=True)
elif DEPLOY_ENVIRONMENT == DeployEnvironment.PRODUCTION:
    # Console logger
    logger.add(sys.stderr, format=PRODUCTION_FORMAT, backtrace=True, diagnose=True)
elif DEPLOY_ENVIRONMENT == DeployEnvironment.TEST:
    # No logging
    pass

# Logtail
LOGTAIL_SOURCE_TOKEN = env("LOGTAIL_SOURCE_TOKEN", None)
# if LOGTAIL_SOURCE_TOKEN:
#     from logtail import LogtailHandler

#     logger.info("Adding logtail handler...")
#     logtail_handler = LogtailHandler(source_token=LOGTAIL_SOURCE_TOKEN)
#     logger.add(logtail_handler, format=PRODUCTION_FORMAT, backtrace=False, diagnose=False)


## Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": env.dj_db_url("DATABASE_URL"),
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

## Cache

REDIS_URL = env("REDIS_URL", None)
if DEPLOY_ENVIRONMENT == DeployEnvironment.PRODUCTION:
    if REDIS_URL:
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379",
            }
        }
    else:
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
logger.info("Using cache backend: " + CACHES["default"]["BACKEND"])

## Sessions

if REDIS_URL:
    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
else:
    SESSION_ENGINE = "django.contrib.sessions.backends.db"

logger.info("Using session engine: " + SESSION_ENGINE)


## Auth

AUTH_USER_MODEL = "teams.User"

# https://docs.djangoproject.com/en/5.0/topics/auth/customizing/
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by email
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
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

LOGIN_REDIRECT_URL = "puzzle_list"

# allauth

ACCOUNT_ADAPTER = "huntsite.teams.adapter.AccountAdapter"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_FORMS = {"signup": "huntsite.teams.forms.SignupForm"}

# Custom
ACCOUNT_DISABLE_REGISTRATION = env.bool("ACCOUNT_DISABLE_REGISTRATION", default=False)

## Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True
# DATE_FORMAT = "F j, Y"
# TIME_FORMAT = "h:i:s A e (O)"
# DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

## Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_ROOT = BASE_DIR / ".staticfiles"
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

## Media files
MEDIA_ROOT = BASE_DIR / ".mediafiles"
MEDIA_URL = "media/"

## Storages

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

## Django 5 transition setting
# https://adamj.eu/tech/2023/12/07/django-fix-urlfield-assume-scheme-warnings/
filterwarnings("ignore", "The FORMS_URLFIELD_ASSUME_HTTPS transitional setting is deprecated.")
FORMS_URLFIELD_ASSUME_HTTPS = True

## Crispy Forms

CRISPY_ALLOWED_TEMPLATE_PACKS = ("bulma",)
CRISPY_TEMPLATE_PACK = "bulma"

## Email

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


## Error Monitoring / Sentry

SENTRY_DSN = env("SENTRY_DSN", None)
if SENTRY_DSN and DEPLOY_ENVIRONMENT != DeployEnvironment.TEST:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        auto_session_tracking=False,
        traces_sample_rate=0.01,
        release="1.0.0",
        environment=DEPLOY_ENVIRONMENT,
    )

## HTML Meta Tag Data

META_TITLE = env("META_TITLE")
META_DESCRIPTION = env("META_DESCRIPTION")
META_AUTHOR = env("META_AUTHOR")
META_KEYWORDS = env("META_KEYWORDS")
META_OG_IMAGE = env("META_OG_IMAGE")

## Hunt state

HUNT_IS_LIVE_DATETIME = env.datetime("HUNT_IS_LIVE_DATETIME", default=timezone.now().isoformat())
if HUNT_IS_LIVE_DATETIME.tzinfo is None:
    HUNT_IS_LIVE_DATETIME = HUNT_IS_LIVE_DATETIME.replace(tzinfo=datetime.timezone.utc)
