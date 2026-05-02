## Project Overview

Weeb API — Django REST Framework backend serving the Weeb showcase site (`../weeb_Front/`). Provides blog, contact, user auth, and a sentiment analysis classifier.

**Stack**: Django 5.2 + DRF + djangorestframework-simplejwt (JWT auth) + scikit-learn (sentiment model) + PostgreSQL (prod) / SQLite (dev) + Gunicorn + WhiteNoise + Sentry

## Commands

All Django commands run from the `weebapi/` directory:

```bash
python manage.py runserver        # Start dev server on :8000
python manage.py migrate          # Apply migrations
python manage.py makemigrations   # Generate migrations — ASK THE USER before running. It diffs models against the DB and writes files; an interactive review is safer.
python manage.py createsuperuser  # Create an admin user
python manage.py test blog users contact   # Run app tests
python manage.py collectstatic --noinput   # Collect static (production)
ruff check weebapi/               # Lint
ruff check weebapi/ --fix         # Lint + auto-fix
```

## Conventions (must follow)

- **Language**: All code is in ENGLISH — model fields, function names, class names, docstrings, commit messages. User-facing API error/validation messages may stay French if that's already the convention in a given app, but new strings default to English.
- **Settings split**: Three files in `core/settings/` — `base.py` (shared), `development.py` (default, SQLite, DEBUG=True), `production.py` (Postgres, HTTPS, WhiteNoise, Sentry). The active module is selected via `DJANGO_SETTINGS_MODULE`. Never put dev-only or prod-only config in `base.py`.
- **Custom user model**: `users.User` with `USERNAME_FIELD = "email"`. `username` is auto-set to the email in `CustomUserManager.create_user`. New users are active by default (inherited from `AbstractUser`). In foreign keys, always reference `settings.AUTH_USER_MODEL`, never `User` directly (pattern: `blog.Post.author`).
- **Auth**: JWT via `rest_framework_simplejwt` only. Tokens at `/api/token/`, refresh at `/api/token/refresh/`, verify at `/api/token/verify/`. No session auth on API routes. Default DRF auth class is `JWTAuthentication`.
- **Permissions per method**: For mixed read/write views, override `get_permissions()` to return `AllowAny` on GET and `IsAuthenticated` (+ object-level perm) on writes. Pattern: see `blog/views.py`. The DRF default `DEFAULT_PERMISSION_CLASSES` is `AllowAny`, so write protection MUST be set explicitly on every write endpoint.
- **Object-level perms**: For per-row write protection, use `IsOwnerOrReadOnly` from `blog/permissions.py` (or write a similar one in the relevant app). Don't rely on view-level perms alone for resources that have an owner.
- **Querysets**: Always filter `is_published=True` (or equivalent visibility flag) on public list endpoints. Never return unpublished/draft data to anonymous users.
- **Slugs**: `Post.save()` auto-generates a unique slug from the title with a numeric suffix on collision. Don't set `slug` manually unless you also handle uniqueness — let `save()` do it.
- **Serializers**: One serializer per resource, in `<app>/serializers.py`. Implicit fields (e.g. `author`) MUST be set in `perform_create(self, serializer)` — never accept them from the request body.
- **URL prefixes**: All API routes mount under `/api/` via `core/urls.py`. App-level `urls.py` declares paths *without* the `api/` prefix.
- **Migrations**: Always commit migration files. When schema changes touch existing rows and defaults aren't safe, write a data migration. Per-file ignores `E501,F401` are already configured for migrations in ruff.
- **Lint**: `ruff` (config in `pyproject.toml`, line-length 100, target py312). Run before commits. The repo intentionally ignores `N806` and `N815` because of legacy field names like `readTime` — don't remove those ignores without renaming the fields and writing a migration.
- **Secrets**: Never commit `.env`. `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `SENTRY_DSN` come from environment variables in production. See `core/load_env.py` and the README for the full list.
- **CORS**: Frontend origins must be added to `CORS_ALLOWED_ORIGINS` in production settings. Never use `CORS_ALLOW_ALL_ORIGINS = True` in production.
- **CSP**: A `ContentSecurityPolicyMiddleware` is wired in `core/middleware.py`. When introducing new external resources (CDN, fonts, analytics), update its directives — don't bypass it.
- **Health check**: `/health/` must keep returning `{"status": "ok"}`. It's used by PaaS health checks. Don't put auth or rate-limiting in front of it.
- **Tests**: Co-locate as `<app>/tests.py`. Run with `python manage.py test <app>`. Use DRF's `APITestCase` for endpoints; create users via `User.objects.create_user(email=..., password=...)` (NOT the bare manager — go through the app's user factory).
- **Pagination**: DRF default `PageNumberPagination`, `PAGE_SIZE = 6`. Override per view if a list needs different pagination behavior — don't change the global default without a reason.

## Architecture (key things to know)

- **Apps**:
  - `blog` — `Post` model, list/create + retrieve/update/destroy views, slug-based lookup, category enum, owner-or-readonly write perm.
  - `contact` — single POST endpoint for the contact form.
  - `users` — custom `User` model (email login, inactive by default), `create_user` and `me` views.
  - `satisfaction` — sentiment analysis used **internally**, not exposed as an HTTP endpoint. `analyze_satisfaction_binary(message)` is called from `Contact.save()` (see `contact/models.py`) to compute a sentiment score (1 = positive, 0 = negative/empty) on every contact submission. The classifier (`sentiment_model.joblib`) is a TF-IDF + Random Forest model loaded at import time.
- **Auth flow**: register at `POST /api/users/create/` (active user by default) → `POST /api/token/` for access + refresh → `Authorization: Bearer <access>` on subsequent requests → `/api/users/me/` to fetch the current user.
- **JWT lifetimes**: 60 min access / 7 days refresh in `base.py`. Tighten in `production.py` (15 min / 1 day per the README).
- **Production stack**: Gunicorn serves WSGI from `core.wsgi:application`, WhiteNoise serves static files, Sentry SDK reports errors when `SENTRY_DSN` is set. Errors can be triggered manually for testing via `/error/` (staff-only).
- **Database**: SQLite (`db.sqlite3`) in dev, PostgreSQL via `DATABASE_URL` (parsed by `dj-database-url`) in prod.
