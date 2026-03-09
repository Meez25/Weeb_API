"""
Utility to load environment variables from .env file
Use this file in manage.py and wsgi.py for production
"""

from pathlib import Path

from dotenv import load_dotenv

# Determine the project base directory (go up two levels to reach project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load the .env file
env_path = BASE_DIR / '.env'

if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Environment variables loaded from {env_path}")
else:
    print(f"⚠ .env file not found at {env_path}")
    print("  Create a .env file based on .env.example")
