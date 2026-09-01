# FastAPI service — Workboard backend

Modules 05–09 built on top of the starter to produce a production-shaped FastAPI service with versioned routes, Pydantic schemas, SQLAlchemy 2.0 models, Alembic migrations, argon2 authentication, JWT + HTTP-only cookie refresh, CORS, and a full pytest suite.

## Quality gates

```bash
make backend-test
```

Or directly:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest --cov=app --cov-fail-under=80
ruff check .
ruff format --check .
mypy app
```

## Key decisions

- Routes handle HTTP concerns only; services own business rules; repositories own query mechanics.
- Pydantic schemas are the external contract; SQLAlchemy models are persistence structures — never share them.
- All database changes go through an Alembic migration.
- `CORSMiddleware` allows `localhost:3000` in development; production origins are set via environment variable.
