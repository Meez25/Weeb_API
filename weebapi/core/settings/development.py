"""
Django development settings.
"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-we^z39&65o$v$nfp#ykca)w&ez1+*mev(a5@o4v3o-0ga#$ibl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS for local development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
]

# JWT signing key (uses SECRET_KEY by default)
SIMPLE_JWT = {
    **SIMPLE_JWT,
    "SIGNING_KEY": SECRET_KEY,
}
