# CaseFlow AI / NZ Property Settlement Review Copilot

## Product

This project builds a production-style AI document workflow platform.

The first domain pack is:
NZ Property Settlement Review Copilot.

The product helps New Zealand property/conveyancing law firms review messy settlement document packs and turn them into ready-to-review matters.

Initial matter types:
1. Individual buyer + bank mortgage
2. Individual vendor + mortgage discharge
3. Trust buyer + mortgage + CDD complexity
4. Trust vendor + deed variation + discharge complexity

## Product Boundaries

This is not an AI lawyer.

The system must not:
- provide final legal advice
- approve settlement readiness
- approve AML/CDD
- submit Landonline instruments
- release settlement funds
- send external emails without human approval
- use real client data in tests

The system should:
- classify uploaded documents
- extract key fields
- run checklist review
- generate missing / unclear items
- create evidence maps with citations
- answer questions using matter-scoped RAG
- draft follow-up emails for human approval
- write audit logs

## Tech Stack

Backend:
- Python
- FastAPI
- Pydantic
- SQLAlchemy or SQLModel
- Alembic
- PostgreSQL
- pgvector

Frontend:
- Next.js
- TypeScript
- Tailwind
- shadcn/ui

AI:
- OCR / document parsing
- embeddings
- pgvector retrieval
- structured extraction
- checklist engine
- bounded agentic workflow
- answer with citations
- insufficient-evidence refusal

Cloud target:
- Azure

## Architecture Principles

- This is not a generic PDF chatbot.
- This is a domain-specific document review workflow.
- RAG must be scoped by organisation_id and matter_id.
- All important AI conclusions must link back to source document and page.
- Low-confidence or missing evidence must produce unclear / needs_human_review.
- LLMs can extract and explain, but deterministic rules should handle hard checks.
- External actions require human approval.
- Every state-changing action must write an audit log.

## Engineering Rules

- Use type hints in Python.
- Use Pydantic schemas for API inputs and outputs.
- Use database migrations for schema changes.
- Every retrieval query must filter by organisation_id and matter_id.
- Every AI conclusion must include source document and page citation.
- If evidence is insufficient, mark the item as unclear or needs_human_review.
- Every state-changing API must write an audit log.
- Every feature must include tests.
- Never commit secrets.
- Never use real legal client files.
- Synthetic demo documents must be clearly marked as synthetic.

## Testing Rules

Backend:
- pytest
- ruff
- mypy where practical

Frontend:
- TypeScript checks
- basic component tests later
- Playwright later for end-to-end demo

AI Evaluation:
- document classification accuracy
- field extraction accuracy
- citation accuracy
- missing item recall
- matter isolation tests
- insufficient-evidence refusal tests

## Definition of Done

A task is not complete unless:
- tests are added or updated
- pytest passes
- ruff passes
- mypy passes where applicable
- no secrets are committed
- AI output has citation or unclear status
- retrieval code enforces tenant and matter isolation
- the agent summarises changed files and remaining risks
