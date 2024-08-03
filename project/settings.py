"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import datetime
from pathlib import Path
from warnings import filterwarnings

from django.utils import timezone
from environs import Env

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

## Security

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

if env("BASE_URL", ""):
    BASE_URL = env("BASE_URL")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", [])

RENDER_EXTERNAL_HOSTNAME = env("RENDER_EXTERNAL_HOSTNAME", "")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INTERNAL_IPS = env.list("INTERNAL_IPS", [])

## Applications

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
    # Third-party apps
    "allauth",
    "allauth.account",
    "crispy_forms",
    "crispy_bulma",
    "debug_toolbar",
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
                "huntsite.context_processors.santa_missing",
                "huntsite.context_processors.user",
                "huntsite.tester_utils.context_processors.time_travel",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


## Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": env.dj_db_url("DATABASE_URL"),
}

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

## allauth

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_FORMS = {"signup": "huntsite.teams.forms.SignupForm"}

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

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

## Django 5 transition setting
# https://adamj.eu/tech/2023/12/07/django-fix-urlfield-assume-scheme-warnings/
filterwarnings("ignore", "The FORMS_URLFIELD_ASSUME_HTTPS transitional setting is deprecated.")
FORMS_URLFIELD_ASSUME_HTTPS = True

## Custom stuff

CRISPY_ALLOWED_TEMPLATE_PACKS = ("bulma",)
CRISPY_TEMPLATE_PACK = "bulma"

## TODO MAKE SURE THIS IS FINE
X_FRAME_OPTIONS = "SAMEORIGIN"


LOGIN_REDIRECT_URL = "puzzle_list"
# LOGOUT_REDIRECT_URL = "home"


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

## Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env("DJANGO_LOG_LEVEL", "INFO"),
        },
    },
}

## HTML Meta Tag Data

META_TITLE = env("META_TITLE")
META_DESCRIPTION = env("META_DESCRIPTION")
META_AUTHOR = env("META_AUTHOR")
META_KEYWORDS = env("META_KEYWORDS")
META_OG_IMAGE = env("META_OG_IMAGE")

HUNT_IS_LIVE_DATETIME = env.datetime("HUNT_IS_LIVE_DATETIME", default=timezone.now().isoformat())
if HUNT_IS_LIVE_DATETIME.tzinfo is None:
    HUNT_IS_LIVE_DATETIME = HUNT_IS_LIVE_DATETIME.replace(tzinfo=datetime.timezone.utc)
