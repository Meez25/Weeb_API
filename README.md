# Weeb_API

# Clone the repo 

- `cd /path/to/put/project/in`
- `git clone https://github.com/Meez25/Weeb_API.git`
- `cd Weeb_API`

#### Create virtual env

- `cd /path/to/Weeb_API`
- `python -m venv venv`
- Activate the environement `source venv/bin/activate` #windows: venv\Scripts\activate
- To disable the environement, `deactivate`

#### Run the project

- `cd /path/to/Weeb_API`
- `source venv/bin/activate`
- `pip install --requirement requirements.txt`
- Copy `.env.example` to `.env` and fill in the values
- `cd weebapi && python manage.py runserver`
- Go to `http://localhost:8000` in a browser.

#### CORS

- `http://localhost:5173`
- `http://127.0.0.1:5173`

## Authentication

#### POST (get token) :
- `/api/token/`

```json
{ "email": "user@example.com", "password": "password" }
```
Response :
```json
{ "access": "...", "refresh": "..." }
```

#### POST (refresh token) :
- `/api/token/refresh/`
```json
{ "refresh": "..." }
```

##  USERS endpoint : 

#### POST (create account) :
- `/api/users/create/`
```json
{ "email": "user@example.com", "first_name": "First", "last_name": "Last", "password": "password" }
```

#### GET (my profile, authenticated) :
- `/api/users/me/`


# Working endpoint :

## CONTACT endpoint
- `/api/contact/`

```json
{
    "first_name": "FIRSTNAME",
    "last_name": "LASTNAME",
    "phone_number": "XXXXXXXXXX",
    "email_address": "example@example.com",
    "message": "Message"
}
```

## BLOG endpoint : 
#### GET/POST : 
- `/api/posts/`

**Query params:**
- `q` — filter by title/excerpt/content/author
- `author` — filter by author name
- `ordering` — sort by `created_at` or `title` (use `-created_at` for desc)
- `page` — pagination (6 posts/page)


#### GET/PATCH/DELETE :
- `/api/posts/<slug>/`


POST example : 
```json
{
  "title": "Recette de la tarte aux pommes",
  "excerpt": "Meilleure tarte du monde",
  "content": "Ingrédients : pâte feuilleté, pommes, compote de pomme ",
  "is_published": true
}
```

## Satisfaction endpoint

#### POST :
- `/api/satisfaction/`

POST example :
```json
{
  "message": "This is great!"
}
```

Response :
```json
{
  "satisfaction": 1
}
```
