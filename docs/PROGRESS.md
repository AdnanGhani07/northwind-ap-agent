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
- [x] Postgres database configured (Supabase instance added to `.env`).
- [x] Local storage directory (`data/storage`) configured for offline zero-cost document storage.
- [ ] Google Gemini API Key: replace placeholder in `.env` when ready for Phase 2/3 LLM tasks.

---

## Phase 1: Scenario, Discovery, Data Generation
**Date:** 2026-10-05

### What Changed
- Authored the comprehensive discovery document [docs/discovery.md](discovery.md) adhering to Appendix A (customer profile: Northwind Industrial Supply Co., 250 vendors, ~1,800 invoices/month, 6 clerks; stakeholder map; 5 simulated interview notes with realistic contradictions; 4-step current process; cost-ranked pain points; metrics; constraints; 3-stage rollout).
- Created Pydantic data models in `data/generators/schema.py` for vendors, POs, goods receipts, invoice line items, ground truth annotations, and typed match outcomes/resolutions.
- Built ReportLab multi-template PDF generator in `data/generators/pdf_generator.py` supporting 5 distinct visual layout templates with realistic styling.
- Created seeded master generator `data/generators/generate_data.py`:
  - Generates 250 vendors with dirty variants and Latin-1 accented records.
  - Generates 900 POs and goods receipts exported to messy ERP CSVs (mixed dates `MM/DD/YYYY` and `DD/MM/YYYY`, whitespace quirks, Latin-1 encoding, renamed columns).
  - Generates 800 PDF invoices + 100 email-body invoices.
  - Injects exact labeled problem distributions matching the plan (3% exact duplicates, 2% near duplicates, 4% price variance, 4% qty mismatch, 2% missing PO, 3% wrong vendor, 1% currency mismatch, ~81% clean matches).
  - Partitions dataset into locked 150-invoice test split (`data/ground_truth/test_split.json`) and 750-invoice dev split (`data/ground_truth/dev_split.json`).
- Authored `tests/test_data_generators.py` verifying full dataset counts, CSV decodability, ground truth schemas, and problem distribution rates.
- Verified test suite (`6 passed in 0.23s`) and linter (`All checks passed!`).

### Decisions Made
- **ReportLab Templating**: Implemented 5 distinct templates (`standard_grid`, `minimal_modern`, `classic_boxed`, `industrial_compact`, `scan_fax`) generating 800 PDFs in under 20 seconds.
- **Messy ERP Format Fidelity**: Simulated realistic legacy enterprise quirks using mixed date formats across even/odd IDs and a dedicated Latin-1 file to test encoding resilience.
- **Split Rigor**: The 150 test split is partitioned by deterministic index and locked in its own JSON file to prevent prompt/model overfitting during Phase 2-4.

### Open Issues / Next Steps
- Ready for Phase 2: Intake service upload endpoint, PDF/email document extraction into strict Pydantic schemas, normalization, and deterministic 2-way/3-way matching.


