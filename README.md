# DigiCafe API Service

Django REST API for DigiCafe. It uses SQLite for now and JWT for authentication.

## Requirements

- Python 3.12+

## First-time setup

```bash
cd digicafe-api-service

# 1. Create and activate a virtual environment (skip creating it if .venv already exists)
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your local environment file
cp .env.example .env
```

Then open `.env` and set `DJANGO_SECRET_KEY` to a random value. You can generate one with:

```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

```bash
# 4. Create the database tables
python manage.py migrate
```


```bash
# 5. Create a development admin you can log in with
python manage.py create_dev_admin   # admin@digicafe.test / digicafe-admin
```

Run it again any time to reset that account's password. Pass `--email` and `--password` to
use different details. It refuses to run when `DJANGO_DEBUG` is off.

## Running the server

```bash
source .venv/bin/activate
python manage.py runserver
```

The API runs at **http://localhost:8000**. The Django admin is at http://localhost:8000/admin/.

To use a different port, run e.g. `python manage.py runserver 8080`, and update
`VITE_API_URL` in the frontend's `.env` to match.

## API endpoints

All request and response bodies are JSON with `snake_case` field names.

| Method | Path | Auth | What it does |
|---|---|---|---|
| POST | `/api/auth/signup/` | none | Create an admin account (not used by the frontend). Body: `full_name`, `email`, `employee_id`, `department` (optional), `password`. Returns `user`, `access`, `refresh`. |
| POST | `/api/auth/login/` | none | Body: `email`, `password`. Returns `user`, `access`, `refresh`. |
| POST | `/api/auth/token/refresh/` | none | Body: `refresh`. Returns a new `access` token. |
| GET | `/api/auth/me/` | Bearer token | The signed-in user. |

Send the access token as `Authorization: Bearer <access>`. Access tokens last 30 minutes,
refresh tokens 7 days.

## Running the tests

```bash
python manage.py test
```

## Environment variables (`.env`)

| Variable | Purpose | Example |
|---|---|---|
| `DJANGO_SECRET_KEY` | Secret used for signing (keep private) | random string |
| `DJANGO_DEBUG` | Show detailed error pages | `True` in development |
| `DJANGO_ALLOWED_HOSTS` | Hostnames the server answers to, comma-separated | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | Frontend addresses allowed to call the API, comma-separated | `http://localhost:3000,http://127.0.0.1:3000` |

`.env` is git-ignored. Share changes to the variable list via `.env.example`.

## Useful commands

```bash
python manage.py createsuperuser        # create an admin login
python manage.py makemigrations         # after changing models
python manage.py migrate                # apply migrations
python manage.py startapp <name>        # create a new app
pip freeze > requirements.txt           # after installing a new package
```

## Project layout

```
config/            project settings, root URLs, WSGI/ASGI entry points
users/             custom User model (email login + role), admin profile, auth endpoints
manage.py          Django command-line tool
requirements.txt   pinned Python dependencies
.env.example       template for local environment variables
```
