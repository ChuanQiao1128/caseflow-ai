# Day 1 Implementation Plan

## Goal

Create the project skeleton and enforce engineering discipline from day one.

## Target Outcome

By the end of Day 1:
- repo skeleton exists
- FastAPI app runs
- Next.js app is scaffolded
- docker-compose runs PostgreSQL + pgvector
- database models are started
- first Alembic migration exists
- pytest, ruff, mypy are configured
- health check endpoint works
- first tests pass
- AGENTS.md and project docs exist

## Day 1 Tasks

1. Create monorepo structure
2. Create FastAPI backend skeleton
3. Add PostgreSQL + pgvector docker-compose
4. Add SQLAlchemy/SQLModel base
5. Add Alembic migration setup
6. Add models:
   - Organisation
   - User
   - Matter
   - Document
   - AuditLog
7. Add endpoint:
   - GET /health
8. Add tests:
   - test_health
   - test_model_imports
9. Add ruff, mypy, pytest config
10. Add README with local setup instructions

## Do Not Do on Day 1

- Do not build OCR yet
- Do not build frontend UI beyond skeleton
- Do not call real LLM APIs
- Do not create real legal documents
- Do not deploy to Azure
- Do not use real client data
