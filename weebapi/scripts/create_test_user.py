#!/usr/bin/env python
"""Create a default superuser for local development."""
import os
import sys

# Make sure weebapi/ (parent of scripts/) is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402

if not settings.DEBUG:
    sys.exit(
        "Refusing to create a hardcoded test superuser outside DEBUG mode. "
        "Use `python manage.py createsuperuser` instead."
    )

User = get_user_model()

email = 'test@example.com'
password = 'testpass123'

if User.objects.filter(email=email).exists():
    print(f"User '{email}' already exists")
else:
    User.objects.create_superuser(email=email, password=password)
    print(f"User '{email}' created successfully")

print("\nCredentials:")
print(f"  Email: {email}")
print(f"  Password: {password}")
