# Project Progress Log

## Phase 0: Setup
**Date:** 2026-10-05

### What Changed
- Initialized local Git repository and configured root `.gitignore`.
- Established monorepo directory layout according to architecture: `docs/`, `data/`, `services/` (`intake`, `extraction`, `matching`, `agent`, `mock_erp`), `web/`, `evals/`, `infra/`.
- Authored [README.md](../README.md) featuring project overview, success metrics targets, architecture flow, and setup guide.
- Added [docker-compose.yml](../docker-compose.yml) skeleton providing local Postgres 15 service with persistent volume and health check.
- Added [.env.example](../.env.example) declaring required environment variables (DB, storage, Google Gemini API, safety policy thresholds).
- Created GitHub Actions workflow [.github/workflows/ci.yml](../.github/workflows/ci.yml) for automated linting (`ruff`) and testing (`pytest`).
- Added initial [pyproject.toml](../pyproject.toml) and smoke test [tests/test_smoke.py](../tests/test_smoke.py).

### Decisions Made
- **Monorepo Layout**: Kept Python backend services under `services/` and Next.js frontend in `web/` to match `docs/PLAN.md`.
- **Environment Strategy**: Maintained clear separation between local dev storage (`local`) and cloud storage (`gcs`) with explicit environment switches.
- **Safety Policy Configuration**: Hard-coded safety policy boundaries are exposed as env defaults (`MAX_AUTO_APPROVE_DOLLARS`, `ALLOW_AUTO_APPROVE_DUPLICATES=false`) outside the LLM.

### Open Issues / External Dependencies Needed
- Live credentials/accounts for:
  - Postgres hosted database (Neon / Supabase) or confirm running via local Docker Compose.
  - Google Cloud Project & Google Gemini API Key for extraction and Google ADK exception agent.
  - Cloud Storage Bucket (if deploying to GCP) or use local mock storage.
