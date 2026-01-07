# JWT API - Usage Guide

## 🔑 Authentication Endpoints

### 1. Obtain a token (Login)

```bash
POST http://127.0.0.1:8000/api/token/
Content-Type: application/json

{
    "username": "votre_username",
    "password": "votre_password"
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
    "refresh": "votre_refresh_token"
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
    "token": "votre_access_token"
}
```

## 📝 Usage with Blog API

### Read articles (Public - No authentication required)

```bash
GET http://127.0.0.1:8000/api/posts/
```

### Create an article (Authentication required)

```bash
POST http://127.0.0.1:8000/api/posts/
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
    "title": "My article",
    "content": "Article content",
    "author": "Author name",
    "excerpt": "Optional summary"
}
```

### Update an article (Authentication required)

```bash
PUT http://127.0.0.1:8000/api/posts/<slug>/
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
    "title": "Modified title",
    "content": "Modified content"
}
```

### Delete an article (Authentication required)

```bash
DELETE http://127.0.0.1:8000/api/posts/<slug>/
Authorization: Bearer <your_access_token>
```

## ⚙️ JWT Configuration

### Token Lifetime

- **Access Token:** 60 minutes
- **Refresh Token:** 7 days

### Enabled Features

- ✅ Automatic refresh token rotation
- ✅ Token blacklist after rotation
- ✅ HS256 Algorithm (HMAC with SHA-256)

## 🔐 Permissions

| Endpoint             | Méthode   | Permission                      |
| -------------------- | --------- | ------------------------------- |
| `/api/posts/`        | GET       | Public (AllowAny)               |
| `/api/posts/`        | POST      | Authenticated (IsAuthenticated) |
| `/api/posts/<slug>/` | GET       | Public (AllowAny)               |
| `/api/posts/<slug>/` | PUT/PATCH | Authenticated (IsAuthenticated) |
| `/api/posts/<slug>/` | DELETE    | Authenticated (IsAuthenticated) |

## 🧪 Example with PowerShell

```powershell
# 1. Obtain a token
$body = @{username='testuser';password='testpass123'} | ConvertTo-Json
$tokenResponse = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/token/' -Method POST -Body $body -ContentType 'application/json'
$tokens = $tokenResponse.Content | ConvertFrom-Json

# 2. Use the token to create an article
$headers = @{Authorization="Bearer $($tokens.access)"}
$articleBody = @{
    title='My article'
    content='My article content'
    author='John Doe'
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/posts/' -Method POST -Headers $headers -Body $articleBody -ContentType 'application/json'
```

## 🧪 Example with curl

```bash
# 1. Obtain a token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'

# 2. Create an article (replace YOUR_TOKEN)
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My article","content":"Content","author":"John Doe"}'
```

## 👤 Test User

A test user has been created:

- **Username:** testuser
- **Password:** testpass123
- **Email:** test@example.com

## 📚 Additional Documentation

For more information on djangorestframework-simplejwt:
https://django-rest-framework-simplejwt.readthedocs.io/
