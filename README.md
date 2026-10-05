# Northwind AP Invoice Reconciliation Agent

> **Forward Deployed Engineer (FDE) Portfolio Project**  
> Simulating an embedded engineering engagement with Northwind Industrial Supply to solve accounts payable backlog through an eval-gated AI agent system.

---

## Executive Summary

Northwind Industrial Supply processes ~1,800 invoices/month across 250 suppliers with 6 AP clerks against a legacy ERP system, resulting in chronic month-end close overruns. 

This repository implements an end-to-end, safety-first AP invoice automation pipeline:
- **Intake & Extraction**: Converts heterogeneous PDFs and email bodies into strict Pydantic schemas.
- **Deterministic 2-Way & 3-Way Matching**: Audits invoice line items against POs and Goods Receipts with configurable tolerance bands without non-deterministic LLM variance.
- **Exception Agent (Google ADK)**: Reasons over mismatches, gathers evidence, drafts vendor inquiries, and recommends resolutions.
- **Hardened Safety Policy**: Enforces strict out-of-LLM guardrails (dollar thresholds, duplicate locks, allow-listed resolutions).
- **Human-in-the-Loop Web UI**: Next.js workspace for clerk review, one-click approvals, and audit log generation.
- **Eval-Gated CI**: Continuous evaluation blocking prompt regressions and tracking accuracy metrics on every commit.

---

## Success Metrics (Target vs. Actual)

| Metric | Target | Baseline (Dev Set) | Final Status |
|---|---|---|---|
| **Extraction Field Accuracy** | `>= 95%` | *Pending Phase 2* | - |
| **Match/Exception Classification Accuracy** | `>= 98%` | *Pending Phase 2* | - |
| **Agent Action Accuracy on Exceptions** | `>= 85%` | *Pending Phase 3* | - |
| **Auto-Resolution Rate** | `60% - 70%` | *Pending Phase 3* | - |
| **False Auto-Approval Rate** | **`< 1%` (Critical Safety Gate)** | *Pending Phase 3* | - |
| **Cost per Invoice** | Track & report | *Pending Phase 2* | - |
| **p95 Latency per Invoice** | Track & report | *Pending Phase 2* | - |
| **Adversarial / Injection Defense** | `10 / 10 handled safely` | *Pending Phase 3* | - |

---

## Architecture Flow

```
                      +-------------------+
                      | Inbound PDF/Email |
                      +---------+---------+
                                |
                                v
                      +-------------------+
                      | Extraction Engine | (LLM + Pydantic + Tiers)
                      +---------+---------+
                                |
                                v
                      +-------------------+
                      |   Normalization   | (Dates, Currency, Vendors)
                      +---------+---------+
                                |
                                v
                      +-------------------+
                      | Matching Engine   | (Deterministic 2-Way/3-Way)
                      +----+---------+----+
                           |         |
               Clean Match |         | Exception (Typed Mismatch)
                           v         v
         +-------------------+     +--------------------------+
         | Auto-Post to ERP  |     | Exception Agent (ADK)    |
         +-------------------+     +------------+-------------+
                                                |
                                                v
                                   +--------------------------+
                                   | Hardened Safety Policy   |
                                   +----+----------------+----+
                     Allowed Low-Risk   |                | Requires Review
                                        v                v
                         +-------------------+     +------------------+
                         | ERP Safe Postback |     | Human Review UI  |
                         +-------------------+     +------------------+
```

---

## Repository Structure

```
northwind-ap-agent/
├── docs/            # Discovery doc, architecture, runbook, PLAN.md, PROGRESS.md
├── data/            # Generators, raw samples, labeled ground truth
│   ├── generators/  # Reproducible synthetic data generation scripts
│   ├── samples/     # Multi-template invoice PDFs and email bodies
│   └── ground_truth/# Golden JSON annotations and split definitions
├── services/        # Backend microservices (Python / FastAPI)
│   ├── intake/      # File upload and mailbox ingestion
│   ├── extraction/  # Document parsing and schema extraction
│   ├── matching/    # Deterministic matching engine (2-way / 3-way)
│   ├── agent/       # Google ADK exception agent + safety policy layer
│   └── mock_erp/    # Simulated legacy ERP with rate limits and 503s
├── web/             # Review UI (Next.js + TypeScript + Tailwind)
├── evals/           # Evaluation runners, regression tests, and benchmarks
└── infra/           # Docker Compose, Dockerfiles, Cloud Run configurations
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ (for Web UI)
- Docker & Docker Compose
- Postgres 15+ (local container or Neon/Supabase)

### Local Environment Setup
```bash
# Clone the repository
git clone <repo-url>
cd northwind-ap-agent

# Copy environment template
cp .env.example .env

# Spin up local infrastructure (Postgres, Mock ERP, Services)
docker compose up -d
```

---

## Development Guidelines

All development strictly follows the rules outlined in [AGENTS.md](file:///d:/Projects/FDE%20Projs/northwind-ap-agent/AGENTS.md) and the phased roadmap in [docs/PLAN.md](file:///d:/Projects/FDE%20Projs/northwind-ap-agent/docs/PLAN.md).
Progress updates and architectural decisions are tracked in [docs/PROGRESS.md](file:///d:/Projects/FDE%20Projs/northwind-ap-agent/docs/PROGRESS.md).
