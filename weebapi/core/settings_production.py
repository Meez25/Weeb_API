"""
Django Production Settings for HTTPS deployment
================================================

This file contains production-specific settings for deploying
the Weeb_API with HTTPS/SSL configuration.

Usage:
    python manage.py runserver --settings=core.settings_production
    
Or set environment variable:
    export DJANGO_SETTINGS_MODULE=core.settings_production
"""

from .settings import *
import os

# ============================================================================
# SECURITY SETTINGS FOR PRODUCTION
# ============================================================================

# CRITICAL: Set to False in production
DEBUG = False

# CRITICAL: Replace with your actual domain(s)
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    'api.yourdomain.com',
    # Add your production domain(s) here
]

# ============================================================================
# SECRET KEY - MUST BE SET VIA ENVIRONMENT VARIABLE
# ============================================================================

# Never commit the production secret key to version control
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable must be set in production")

# ============================================================================
# HTTPS/SSL CONFIGURATION
# ============================================================================

# Redirect all HTTP requests to HTTPS
SECURE_SSL_REDIRECT = True

# Use secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HTTP Strict Transport Security (HSTS)
# Tells browsers to only use HTTPS for the next year
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Prevent browser from guessing content type
SECURE_CONTENT_TYPE_NOSNIFF = True

# Enable XSS protection
SECURE_BROWSER_XSS_FILTER = True

# Clickjacking protection
X_FRAME_OPTIONS = 'DENY'

# SSL/TLS Configuration
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ============================================================================
# CORS CONFIGURATION FOR PRODUCTION
# ============================================================================

# Replace with your production frontend domain(s)
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    # Add your production frontend URL(s) here
]

# Allow credentials (cookies, authorization headers)
CORS_ALLOW_CREDENTIALS = True

# Allowed methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allowed headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# For production, use PostgreSQL instead of SQLite
# Install psycopg2-binary: pip install psycopg2-binary

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'weebapi_db'),
        'USER': os.environ.get('DB_USER', 'weebapi_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}

# Fallback to SQLite if PostgreSQL is not configured (NOT RECOMMENDED)
if not os.environ.get('DB_PASSWORD'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ============================================================================
# STATIC FILES CONFIGURATION
# ============================================================================

STATIC_ROOT = os.path.join(BASE_DIR.parent, 'staticfiles')
STATIC_URL = '/static/'

# Media files (user uploads)
MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')
MEDIA_URL = '/media/'

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR.parent, 'logs', 'django_errors.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ============================================================================
# EMAIL CONFIGURATION (for error notifications)
# ============================================================================

ADMINS = [
    ('Admin Name', 'admin@yourdomain.com'),
]

# Email backend configuration (example with SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'noreply@yourdomain.com')

# ============================================================================
# PERFORMANCE OPTIMIZATIONS
# ============================================================================

# Cache configuration (example with Redis)
# Install: pip install django-redis
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

# Session engine (use cache for better performance)
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"

# ============================================================================
# JWT CONFIGURATION FOR PRODUCTION
# ============================================================================

SIMPLE_JWT = {
    **SIMPLE_JWT,  # Inherit from base settings
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),  # Shorter for production
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),     # Shorter for production
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# ============================================================================
# REST FRAMEWORK PRODUCTION SETTINGS
# ============================================================================

REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # Inherit from base settings
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        # Remove BrowsableAPIRenderer in production
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}

# ============================================================================
# ADDITIONAL SECURITY HEADERS
# ============================================================================

# Content Security Policy (CSP)
# Consider using django-csp package for more granular control
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)

print("🔒 Production settings loaded with HTTPS/SSL configuration")
