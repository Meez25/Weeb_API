# Weeb_API

Django REST API for a blog with contact management and satisfaction analysis.

## Stack

- **Django 5.2** + **Django REST Framework**
- **JWT authentication** via `djangorestframework-simplejwt`
- **CORS** via `django-cors-headers`
- **Sentiment analysis** via a pre-trained scikit-learn model
- **PostgreSQL** (production) / **SQLite** (development)
- **Gunicorn** + **WhiteNoise** (production)

## Project structure

```
weeb_API/
├── weebapi/
│   ├── core/               # Django project (settings, urls, wsgi)
│   │   └── settings/
│   │       ├── base.py         # Common settings
│   │       ├── development.py  # Local dev (SQLite, DEBUG=True)
│   │       └── production.py   # Production (PostgreSQL, WhiteNoise, HTTPS)
│   ├── blog/               # Blog posts app
│   ├── contact/            # Contact form app
│   └── satisfaction/       # Sentiment analysis app
├── requirements.txt
└── .env.example
```

## Quick start

### 1. Clone and set up the virtual environment

```bash
git clone https://github.com/Meez25/Weeb_API.git
cd Weeb_API

python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Generate a secret key and add it to `.env`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Run the development server

```bash
cd weebapi
python manage.py migrate
python manage.py runserver
```

API available at `http://localhost:8000`.

---

## API endpoints

### Authentication (JWT)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/token/` | Obtain access + refresh tokens |
| POST | `/api/token/refresh/` | Refresh access token |
| POST | `/api/token/verify/` | Verify a token |

**Obtain tokens:**

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

**Use the access token:**

```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/posts/
```

**Token lifetimes:**
- Access token: 60 min (development) / 15 min (production)
- Refresh token: 7 days (development) / 1 day (production)

---

### Blog

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts/` | List posts (paginated, 6 per page) |
| POST | `/api/posts/` | Create a post |
| GET | `/api/posts/<slug>/` | Retrieve a post |
| PATCH | `/api/posts/<slug>/` | Update a post |
| DELETE | `/api/posts/<slug>/` | Delete a post |

**Query parameters for GET `/api/posts/`:**

| Parameter | Description |
|-----------|-------------|
| `search` | Filter by title or content |
| `author` | Filter by author name |
| `category` | Filter by category |
| `ordering` | Sort by `created_at` or `title` (prefix `-` for descending) |
| `page` | Page number |

**POST example:**

```json
{
  "title": "Apple Pie Recipe",
  "excerpt": "Best pie in the world",
  "content": "Ingredients: puff pastry, apples, apple sauce...",
  "author": "Chef John",
  "category": "Recipes",
  "is_published": true
}
```

**GET/PATCH/DELETE a post:** `/api/posts/<slug>/`

---

### Contact

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/contact/` | Submit a contact message |

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "0612345678",
  "email_address": "john@example.com",
  "message": "Hello, I have a question..."
}
```

---

### Satisfaction

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/satisfaction/` | Analyze sentiment of a message |

```json
{ "message": "This is great!" }
```

Response:

```json
{ "satisfaction": 1 }
```

| Value | Meaning |
|-------|---------|
| `1` | Positive |
| `0` | Neutral |
| `-1` | Negative |

---

## Deployment

### Settings

The project uses a split settings structure. The default is `development`. In production, override via environment variable.

| File | Used when |
|------|-----------|
| `core.settings.development` | Local development (default) |
| `core.settings.production` | Production |

### Required environment variables (production)

| Variable | Description |
|----------|-------------|
| `DJANGO_SETTINGS_MODULE` | `core.settings.production` |
| `SECRET_KEY` | Django secret key — generate a new one |
| `DATABASE_URL` | PostgreSQL URL: `postgres://user:pass@host:5432/db` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed domains |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of allowed frontend origins |

Copy `.env.example` to `.env` and fill in the values. Never commit `.env` to version control.

### Start command (Gunicorn)

```bash
gunicorn core.wsgi:application --chdir weebapi
```

### First deploy checklist

```bash
# Collect static files
python manage.py collectstatic --noinput

# Apply migrations
python manage.py migrate
```
