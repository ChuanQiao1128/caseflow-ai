# CaseFlow AI Project Brief

## Project Name

CaseFlow AI

## First Domain Pack

NZ Property Settlement Review Copilot

## One-line Description

A domain-specific AI document workflow system that turns messy New Zealand property settlement document packs into ready-to-review matters with structured summaries, missing item checks, evidence maps, citation-backed Q&A, draft follow-up emails, human approval, and audit logs.

## Why This Exists

Property/conveyancing law firms handle repeated document-heavy workflows:
- buyer purchase with mortgage
- vendor sale with mortgage discharge
- trust buyer matters
- trust vendor matters

The bottleneck is not just reading speed. It is document classification, cross-document checking, missing item detection, evidence tracing, and preparing review-ready notes.

## MVP Goal

Build a local production-style MVP that demonstrates:
- document upload
- PostgreSQL + pgvector data model
- synthetic property matter data
- OCR/text ingestion placeholder
- chunking and embeddings
- matter-scoped RAG
- structured field extraction
- buyer/vendor/trust checklist engine
- bounded Settlement Review Agent
- draft follow-up email
- human approval queue
- audit log
- basic evaluation suite

## Not In Scope for MVP

- real client data
- final legal advice
- automatic settlement approval
- Landonline integration
- bank portal integration
- sending real emails
- Actionstep/LEAP integration
- production Azure deployment on Day 1
