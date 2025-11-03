# Weeb_API

# Clone the repo 

- `cd /path/to/put/project/in`
- `git clone https://github.com/Meez25/Weeb_API.git`

#### Create virtual env

- `cd /path/to/Weeb_API`
- `python -m venv venv`
- Activate the environement `source venv/bin/activate`
- To disable the environement, `deactivate`

#### Run the project

- `cd /path/to/Weeb_API`
- `source venv/bin/activate`
- `pip install --requirement requirements.txt`
- `python manage.py runserver`
- Go to `http://localhost:8000` in a browser.


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

#### GET/PATCH/DELETE :
- `/api/posts/<slug>/`


POST example : 
```json
{
  "title": "Recette de la tarte aux pommes",
  "excerpt": "Meilleure tarte du monde",
  "content": "Ingrédients : pâte feuilleté, pommes, compote de pomme ",
  "author": "Maïté",
  "is_published": true
}
```

## Satisfaction endpoint

#### POST :-
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
