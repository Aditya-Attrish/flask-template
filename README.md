# 🔥 Flask Scalable Template

> A production-ready Flask API starter built with software engineering best practices —
> Application Factory Pattern, JWT Auth, Role-Based Access Control, Redis caching,
> multi-environment config, Docker support, and a full test suite out of the box.

---

## ✨ Why This Template?

Most Flask tutorials show a `app.py` with everything crammed in one file. This template shows how Flask applications are **actually built** at scale — properly structured, testable, and ready to grow from MVP to production without rewrites.

| Pattern | Implementation |
|---|---|
| Application Factory | `create_app()` in `app/__init__.py` |
| Blueprints | Versioned API (`/api/v1`) with nested blueprints |
| Service Layer | Business logic decoupled from route handlers |
| Repository Pattern | `BaseModel` with reusable query helpers |
| 12-Factor Config | Environment-specific classes via `config/` |
| JWT Auth | Access + refresh token flow via Flask-JWT-Extended |
| RBAC | `@admin_required`, `@owner_or_admin` decorators |
| Soft Delete | `SoftDeleteMixin` with `.active()` query filter |
| Rate Limiting | Flask-Limiter with Redis backend |
| Caching | Flask-Caching (SimpleCache → Redis in production) |
| CORS | Flask-CORS with origin whitelist |
| Request Logging | Timing + structured logs via middleware |
| Error Handling | Global JSON error handlers for all HTTP codes |
| Testing | Integration + unit tests with pytest |
| Docker | Multi-stage Dockerfile + docker-compose |

---

## 🏗 Project Structure

```
flask-template/
├── app/
│   ├── __init__.py          # Application factory — create_app()
│   ├── extensions/          # Flask extensions initialized once
│   ├── api/
│   │   └── v1/              # Versioned API blueprints
│   │       ├── __init__.py  # Blueprint registry
│   │       ├── health.py    # GET /api/v1/health
│   │       ├── auth.py      # register / login / refresh / me
│   │       └── users.py     # CRUD: list / get / update / delete
│   ├── models/
│   │   ├── base.py          # BaseModel with save/delete/to_dict + mixins
│   │   └── user.py          # User entity (bcrypt, soft-delete, roles)
│   ├── services/
│   │   ├── auth_service.py  # Registration, login, token identity
│   │   └── user_service.py  # Paginated list, update, soft-delete
│   ├── middleware/          # Request timing, global error handlers
│   └── utils/
│       ├── responses.py     # Consistent success/error JSON envelope
│       ├── validators.py    # Email, username, password validation
│       └── decorators.py    # @admin_required, @owner_or_admin, @validate_json
├── config/
│   └── __init__.py          # Development / Testing / Staging / Production
├── tests/
│   ├── unit/
│   │   └── test_user_model.py
│   └── integration/
│       └── test_auth.py
├── migrations/              # Flask-Migrate / Alembic migrations
├── .env.example
├── Dockerfile               # Multi-stage production image
├── docker-compose.yml       # App + PostgreSQL + Redis
├── requirements.txt
└── wsgi.py                  # Gunicorn entry point
```

---

## 🚀 Quick Start

### 1. Clone & set up environment

```bash
git clone https://github.com/Aditya-Attrish/flask-template.git
cd flask-template

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL
```

### 3. Initialize the database

```bash
flask db init          # First time only
flask db migrate -m "Initial migration"
flask db upgrade
```

### 4. Run the server

```bash
flask run --debug
```

API is now live at **http://localhost:5000**

---

## 🐳 Docker (Recommended)

Spin up Flask + PostgreSQL + Redis with one command:

```bash
docker-compose up --build
```

The app will be available at **http://localhost:5000** with hot-reload enabled.

---

## 📡 API Reference

All responses use a consistent envelope:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Auth endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/auth/register` | — | Create account |
| `POST` | `/api/v1/auth/login` | — | Get access + refresh tokens |
| `POST` | `/api/v1/auth/refresh` | Refresh token | Rotate access token |
| `GET`  | `/api/v1/auth/me` | Bearer token | Current user |

### User endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET`    | `/api/v1/users/` | Admin | Paginated user list |
| `GET`    | `/api/v1/users/:id` | Bearer | Get user by ID |
| `PATCH`  | `/api/v1/users/:id` | Owner / Admin | Update profile |
| `DELETE` | `/api/v1/users/:id` | Owner / Admin | Soft-delete account |

### Health

```
GET /api/v1/health
```
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "checks": { "database": "ok" }
}
```

---

## 🧪 Testing

```bash
make test          # Run full suite
make coverage      # Run with coverage report
```

Tests use an **in-memory SQLite database** and are fully isolated — no external services required.

```
tests/
├── unit/
│   └── test_user_model.py   # Password hashing, to_dict, soft-delete
└── integration/
    └── test_auth.py          # Register, login, /me, edge cases
```

---

## ⚙️ Configuration

Configurations are class-based and selected via `FLASK_ENV`:

| `FLASK_ENV` | Class | Database | Cache |
|---|---|---|---|
| `development` | `DevelopmentConfig` | SQLite | In-memory |
| `testing` | `TestingConfig` | SQLite in-memory | In-memory |
| `staging` | `StagingConfig` | PostgreSQL (env var) | Redis |
| `production` | `ProductionConfig` | PostgreSQL (env var) | Redis |

---

## 🔐 Security Features

- **Password hashing** — bcrypt with auto-generated salt
- **JWT tokens** — short-lived access tokens (1h) + refresh tokens (30d)
- **Rate limiting** — per-IP limits, configurable per environment
- **CORS** — origin whitelist, tighter in production
- **Soft delete** — user data is never permanently removed on delete
- **Role-based access** — `admin`, `moderator`, `user` roles
- **Input validation** — `@validate_json` decorator on all POST routes

---

## 🏭 Production Deployment

```bash
# Run with Gunicorn (4 worker processes)
gunicorn "wsgi:app" --workers 4 --bind 0.0.0.0:8000 --timeout 120

# With Docker
docker build -t flask-template .
docker run -p 8000:8000 --env-file .env flask-template
```

---

## 🗺 Extending This Template

This template is intentionally minimal. Here's how to add common features:

| Feature | Where to add |
|---|---|
| New resource (e.g. `Post`) | `app/models/post.py` → `app/services/post_service.py` → `app/api/v1/posts.py` |
| Email sending | `app/services/email_service.py` + Flask-Mail |
| File uploads | `app/services/storage_service.py` + S3/Cloudinary |
| Background tasks | Celery + Redis worker |
| Admin dashboard | Flask-Admin or a separate admin blueprint |
| API docs | Flask-Smorest or Flasgger (OpenAPI/Swagger) |
| WebSockets | Flask-SocketIO |

---

## 📦 Tech Stack

| Library | Purpose |
|---|---|
| Flask 3.1 | Web framework |
| SQLAlchemy + Flask-Migrate | ORM + Alembic migrations |
| Flask-JWT-Extended | JWT auth |
| bcrypt | Password hashing |
| Flask-Limiter | Rate limiting |
| Flask-Caching | Response caching |
| Flask-CORS | Cross-origin headers |
| Flask-Marshmallow | Schema serialization |
| Gunicorn | Production WSGI server |
| pytest | Testing |
| Docker + Compose | Containerization |

---

## 📄 License

MIT License — free to use for personal and commercial projects.

---

*Built to demonstrate Flask architecture patterns. Feel free to use this as a starting point for your own APIs.*
