# Starter FastAPI service

This intentionally small service establishes the process, configuration, database connection, and health-check conventions used by the workshop. Modules 05–09 replace this baseline with versioned routers, schemas, models, migrations, services, repositories, authentication, and a layered test suite.

## Local verification

From the exported starter repository:

```bash
make backend-test
```

For a direct Python workflow, provide a reachable `DATABASE_URL`, then run:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
```

The starter test protects liveness without requiring PostgreSQL. Readiness deliberately checks the real database dependency.
