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

## Local backend setup

The Day 1 backend lives in `apps/api` and uses `uv`.

Prerequisites:
- Python 3.12+
- `uv`
- Docker + Docker Compose

1. Start PostgreSQL with pgvector:

```bash
docker compose up -d db
```

2. Install backend dependencies:

```bash
cd apps/api
uv sync --extra dev
```

3. Copy environment variables:

```bash
cp .env.example .env
```

4. Run the API:

```bash
uv run uvicorn caseflow_api.main:app --reload
```

5. Check the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

6. Run tests and checks:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

7. Create the initial database schema with Alembic:

```bash
uv run alembic upgrade head
```
