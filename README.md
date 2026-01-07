# Weeb_API

Django REST API for a blog with contact management and satisfaction analysis.

## 🚀 Quick Start

### Local Development

#### 1. Clone the repository

```bash
cd /path/to/put/project/in
git clone https://github.com/Meez25/Weeb_API.git
cd Weeb_API
```

#### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run development server

```bash
cd weebapi
python manage.py migrate
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

### Production Deployment with HTTPS

#### To deploy this API in production with HTTPS/SSL, check **[EPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)** :

## 📡 API Endpoints

### 🔑 Authentication (JWT)

The API uses JWT (JSON Web Tokens) for authentication with access and refresh tokens.

#### Obtain Token Pair

**POST** `/api/token/`

Request:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Response:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Refresh Access Token

**POST** `/api/token/refresh/`

Request:

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Response:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Using the Access Token

Include the access token in the `Authorization` header for protected endpoints:

```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  https://api.example.com/api/posts/
```

**Token Lifetimes:**

- **Access Token**: 5 minutes (short-lived for security)
- **Refresh Token**: 1 day (use to obtain new access tokens)

📖 **For more details:** See [JWT_GUIDE.md](weebapi/scripts/JWT_GUIDE.md)

---

### 📧 Contact Endpoint

**POST** `/api/contact/`

Request:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "1234567890",
  "email_address": "john.doe@example.com",
  "message": "Hello, I have a question..."
}
```

---

### 📝 Blog Endpoints

#### List/Create Posts

**GET/POST** `/api/posts/`

**Query parameters:**

- `search` — Filter by title/content
- `author` — Filter by author name
- `category` — Filter by category
- `ordering` — Sort by `created_at` or `title` (use `-created_at` for descending)
- `page` — Pagination (6 posts per page)

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

#### Retrieve/Update/Delete Post

**GET/PATCH/DELETE** `/api/posts/<slug>/`

Example: `/api/posts/apple-pie-recipe/`

---

### 😊 Satisfaction Endpoint

Analyze sentiment of a message using AI.

**POST** `/api/satisfaction/`

Request:

```json
{
  "message": "This is great!"
}
```

Response:

```json
{
  "satisfaction": 1
}
```

**Satisfaction values:**

- `1` = Positive
- `0` = Neutral
- `-1` = Negative
