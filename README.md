# CaseFlow AI

A configurable AI document workflow platform.

First domain pack:

## NZ Property Settlement Review Copilot

This project helps New Zealand property/conveyancing law firms turn messy settlement document packs into ready-to-review matters.

It is not a generic PDF chatbot.

It demonstrates:
- FastAPI
- PostgreSQL + pgvector
- matter-scoped RAG
- structured extraction
- checklist engine
- bounded agentic workflow
- human approval
- audit logging
- synthetic evaluation data
- future Azure deployment

See:
- `AGENTS.md`
- `docs/PROJECT_BRIEF.md`
- `docs/DAY1_PLAN.md`
- `docs/HERMES_WORKFLOW.md`

## Local backend verification

The Day 1 backend lives in `apps/api` and uses `uv`.

Run these commands for local verification:

```bash
cd apps/api
uv sync --extra dev
docker compose up -d db
cp .env.example .env
```

Set `DATABASE_URL` in `apps/api/.env` to use the Docker Postgres host port 55432:

```bash
DATABASE_URL=postgresql+psycopg://caseflow:caseflow@localhost:55432/caseflow
```

Then run the migration, API, and checks:

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
