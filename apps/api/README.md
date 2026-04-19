# CaseFlow API

## Local backend verification

The Day 1 backend lives in `apps/api` and uses `uv`.

Run these commands for local verification:

```bash
docker compose up -d db
cd apps/api
uv sync --extra dev
cp .env.example .env
```

Set `DATABASE_URL` in `apps/api/.env` to use the Docker Postgres host port 55432:

```bash
DATABASE_URL=postgresql+psycopg://caseflow:caseflow@localhost:55432/caseflow
```

Then run the migration, API, and checks from `apps/api`:

```bash
uv run alembic upgrade head
uv run uvicorn caseflow_api.main:app --reload
uv run pytest
uv run ruff check .
uv run mypy src
```

Optional health check:

```bash
curl http://127.0.0.1:8000/health
```
