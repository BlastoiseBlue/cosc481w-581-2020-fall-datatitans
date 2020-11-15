"""
Django settings for datatitan_site project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
from google.cloud import secretmanager
import google.auth
import google.auth.transport.requests
import json
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").casefold() != "false"

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "data-titans.uc.r.appspot.com"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "data.apps.DataConfig",
    "blog.apps.BlogConfig",
    "social_django",
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

ROOT_URLCONF = "datatitan_site.urls"

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
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "datatitan_site.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

POSTGRES_USER = os.getenv("POSTGRES_USER", "DataTitans")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PASSWORD_FILE = os.getenv(
    "POSTGRES_PASSWORD_FILE", BASE_DIR.parent / "cred" / "postgres_password.txt"
)
APP_ENV = os.getenv("APP_ENV")
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("GOOGLE_OAUTH2_SECRET")

if APP_ENV == "docker-compose":
    # Only attempt to access the postgres daemon if you think you're running in a docker container
    with Path(POSTGRES_PASSWORD_FILE).open("r") as file:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "DataTitans",
                "HOST": "db",
                "USER": POSTGRES_USER if POSTGRES_USER else "DataTitans",
                "PASSWORD": file.read(),
                "PORT": "5432",
            }
        }
elif APP_ENV == "google-app-engine":
    creds, project = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    client = secretmanager.SecretManagerServiceClient()
    db_user = client.access_secret_version(
        name=os.getenv("POSTGRES_ACCOUNT_SECRET_ID")
    )
    account = json.loads(db_user.payload.data)
    oauth_credentials = json.loads(client.access_secret_version(
        name=os.getenv("OAUTH_CREDENTIALS_SECRET_ID")
    ).payload.data)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "DataTitans",
            "HOST": "/cloudsql/data-titans:us-central1:datatitan-db"
            if os.getenv("SERVER_SOFTWARE")
            else "localhost",
            "PORT": "5432",
            **account,
        }
    }
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = oauth_credentials["web"]["client_id"]
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = oauth_credentials["web"]["client_secret"]
    SECRET_KEY = client.access_secret_version(name=os.getenv("DJANGO_SECRET_KEY_ID")).payload.data
else:
    with Path(POSTGRES_PASSWORD_FILE).open("r") as file:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "DataTitans",
                "HOST": "localhost",
                "USER": POSTGRES_USER if POSTGRES_USER else "DataTitans",
                "PASSWORD": file.read(),
                "PORT": "5432",
            }
        }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

if APP_ENV == "docker-compose":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": "memcached:11211",
        }
    }
elif APP_ENV == "google-app-engine":
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": "localhost:11211",
        }
    }

AUTHENTICATION_BACKENDS = [
    "social_core.backends.open_id.OpenIdAuth",
    "social_core.backends.google.GoogleOpenId",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.google.GoogleOAuth",
    "django.contrib.auth.backends.ModelBackend",
]

SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/data/"
LOGOUT_REDIRECT_URL = "/data/"
