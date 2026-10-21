# QueryPilot AI

Ask business questions in English, Roman Urdu, or both. QueryPilot retrieves the relevant schema and
business definitions, generates a validated SQL proposal, runs it under a read-only database role, and
explains the result. Built as a 7-day portfolio project; uses synthetic data only.

**Stack:** Flutter Web, FastAPI, LangGraph, SQLGlot, Supabase PostgreSQL (pgvector).

**Security principle:** the LLM proposes; the application and database permissions decide.
Prompts are never a security boundary.

## Status
- [ ] Day 1: Supabase schema, restricted role, Python DB connection
- [ ] Day 2: FastAPI + structured output + provider adapter
- [ ] Day 3: Schema RAG
- [ ] Day 4: LangGraph workflow
- [ ] Day 5: SQL security + evaluation
- [ ] Day 6: Flutter Web
- [ ] Day 7: Deploy + docs + demo

## Backend quick start
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate.bat        # Windows cmd (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env            # then set DATABASE_URL (restricted query_readonly role only)
pytest -q
```

## Project layout
- `backend/` FastAPI app, DB access, tests
- `supabase/` migrations, seed data, database tests
- `evaluation/` golden questions and reports
- `docs/` architecture, security, decisions
- `scripts/` helper scripts

## Safety notes
- Synthetic data only; never commit `.env` or credentials.
- Generated SQL runs only with a read-only, time-limited database role.