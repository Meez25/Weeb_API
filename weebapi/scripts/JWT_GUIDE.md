# JWT API - Usage Guide

## 🔑 Authentication Endpoints

The project's `USERNAME_FIELD` is `email`, so authentication payloads use
`email` (not `username`).

### 1. Obtain a token (Login)

```bash
POST http://127.0.0.1:8000/api/token/
Content-Type: application/json

{
    "email": "your_email@example.com",
    "password": "your_password"
}
```

**Response:**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. Refresh a token

```bash
POST http://127.0.0.1:8000/api/token/refresh/
Content-Type: application/json

{
    "refresh": "your_refresh_token"
}
```

**Response:**

```json
{
  "access": "new_access_token",
  "refresh": "new_refresh_token"
}
```

### 3. Verify a token

```bash
POST http://127.0.0.1:8000/api/token/verify/
Content-Type: application/json

{
    "token": "your_access_token"
}
```

## 📝 Usage with Blog API

### Read articles (Public - No authentication required)

```bash
GET http://127.0.0.1:8000/api/posts/
```

### Create an article (Authentication required)

`author` is set automatically from the authenticated user — do not send it in
the request body.

```bash
POST http://127.0.0.1:8000/api/posts/
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
    "title": "My article",
    "content": "Article content",
    "category": "technologie",
    "excerpt": "Optional summary"
}
```

### Update an article (Authentication required, owner only)

```bash
PUT http://127.0.0.1:8000/api/posts/<slug>/
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
    "title": "Modified title",
    "content": "Modified content"
}
```

### Delete an article (Authentication required, owner only)

```bash
DELETE http://127.0.0.1:8000/api/posts/<slug>/
Authorization: Bearer <your_access_token>
```

## ⚙️ JWT Configuration

### Token Lifetime

| Environment | Access Token | Refresh Token |
| ----------- | ------------ | ------------- |
| Development | 60 minutes   | 7 days        |
| Production  | 15 minutes   | 1 day         |

### Enabled Features

- ✅ Automatic refresh token rotation
- ✅ Token blacklist after rotation
- ✅ HS256 algorithm (HMAC with SHA-256)
- ✅ Throttling on `/api/token/` and `/api/users/create/` (production)

## 🔐 Permissions

| Endpoint             | Method    | Permission                       |
| -------------------- | --------- | -------------------------------- |
| `/api/posts/`        | GET       | Public (AllowAny)                |
| `/api/posts/`        | POST      | Authenticated (IsAuthenticated)  |
| `/api/posts/<slug>/` | GET       | Public (AllowAny)                |
| `/api/posts/<slug>/` | PUT/PATCH | Authenticated + owner only       |
| `/api/posts/<slug>/` | DELETE    | Authenticated + owner only       |

## 🧪 Example with PowerShell

```powershell
# 1. Obtain a token
$body = @{email='test@example.com';password='testpass123'} | ConvertTo-Json
$tokenResponse = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/token/' -Method POST -Body $body -ContentType 'application/json'
$tokens = $tokenResponse.Content | ConvertFrom-Json

# 2. Use the token to create an article
$headers = @{Authorization="Bearer $($tokens.access)"}
$articleBody = @{
    title='My article'
    content='My article content'
    category='technologie'
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/posts/' -Method POST -Headers $headers -Body $articleBody -ContentType 'application/json'
```

## 🧪 Example with curl

```bash
# 1. Obtain a token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# 2. Create an article (replace YOUR_TOKEN)
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My article","content":"Content","category":"technologie"}'
```

## 👤 Test User

`scripts/create_test_user.py` creates a default superuser when run in DEBUG
mode (it refuses to run otherwise):

- **Email:** test@example.com
- **Password:** testpass123

## 📚 Additional Documentation

For more information on djangorestframework-simplejwt:
https://django-rest-framework-simplejwt.readthedocs.io/
