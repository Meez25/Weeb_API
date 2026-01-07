#!/usr/bin/env python
import os
import django

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'testuser'
password = 'testpass123'
email = 'test@example.com'

if User.objects.filter(username=username).exists():
    print(f"✓ User '{username}' already exists")
else:
    User.objects.create_superuser(username, email, password)
    print(f"✓ User '{username}' created successfully!")
    
print(f"\nCredentials:")
print(f"  Username: {username}")
print(f"  Password: {password}")
