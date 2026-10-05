# Discovery Document: Accounts Payable Automation
**Customer:** Northwind Industrial Supply Co.  
**Engagement Type:** Forward Deployed Engineer (FDE) Pilot  
**Author:** FDE Engagement Team  
**Date:** October 2026  
**Status:** Approved for Phase 1 Execution  

---

## 1. Background

Northwind Industrial Supply Co. is a regional Business-to-Business (B2B) distributor of fasteners, precision tooling, Maintenance, Repair, and Operations (MRO) supplies, and safety equipment operating across the Midwest and Pacific Northwest. With 3 distribution hubs, annual revenues of ~$185M, and an active catalog of 42,000 Stock Keeping Units (SKUs), Northwind relies on an established network of approximately 250 active suppliers.

Northwind's Accounts Payable (AP) department processes approximately 1,800 invoices per month. The team consists of 6 full-time Accounts Payable (AP) clerks and an Accounts Payable (AP) Manager operating against a legacy on-premise Enterprise Resource Planning (ERP) system (Northwind Legacy ERP / IBM Application System/400 [AS/400] core derivative). 

Over the past three quarters, increased supplier fragmentation and supply chain volatility have caused Northwind's standard 5-day month-end financial close to consistently overrun by 4 to 6 business days. Invoices arrive across multiple channels (unstructured Portable Document Format [PDF] files, scan-heavy attachments, email bodies) with frequent minor discrepancies in freight, unit pricing, or delivery quantities. Finance leadership requested an embedded Forward Deployed Engineer (FDE) engagement to evaluate automating invoice reconciliation while safeguarding against duplicate or erroneous disbursements.

---

## 2. Stakeholder Map

| Role | Name (Fictional) | Primary Motivation | Concern Regarding Automation |
|---|---|---|---|
| **Corporate Controller** | David Thorne | Accelerate month-end close from 11 days to 4 days; reduce operational overhead. | Erroneous disbursements, Sarbanes-Oxley Act (SOX) compliance failures, lack of auditable decision trails. |
| **Accounts Payable (AP) Manager** | Mark Henderson | Prevent duplicate payments; ensure supplier dispute resolution doesn't slip through cracks. | "Black box" Artificial Intelligence (AI) hallucinating approvals on fuzzy invoice totals without human oversight. |
| **Senior Accounts Payable (AP) Clerk** | Sarah Jenkins | Eliminate tedious line-item data entry; reduce supplier phone/email tag. | Fear of being replaced by Artificial Intelligence (AI); skepticism that software can understand messy supplier templates. |
| **Junior Accounts Payable (AP) Clerk** | Marcus Vance | Reduce backlog pressure during closing week; clear exception pile faster. | Being blamed for automation errors or having to manually fix broken automated batches. |
| **Lead ERP / Information Technology (IT) Admin** | Elena Rostova | Maintain Enterprise Resource Planning (ERP) stability; protect network boundary; avoid brittle database integrations. | Direct database writes corrupting General Ledger (GL) tables; security risks from inbound malicious invoice Portable Document Format (PDF) files. |

---

## 3. Simulated Interview Notes (With Realistic Stakeholder Contradictions)

1. **David Thorne (Corporate Controller):**
   > *"I want 95% of these invoices running straight through to payment without human eyes touching them. We are spending $340k a year in manual clerk hours just re-typing numbers that already exist on our purchase orders (POs). If an invoice is within $50 of the Purchase Order (PO), just pay it. Our cash discount terms (2% discount if paid within 10 days, net due in 30 days [2/10 Net 30]) are being missed constantly."*
   >
   > *(Contradiction: Willing to set high automated dollar tolerances, directly opposing the Accounts Payable [AP] Manager's strict zero-variance policy).*

2. **Mark Henderson (Accounts Payable [AP] Manager):**
   > *"David is too optimistic. If an algorithm auto-approves a $50 discrepancy on 1,800 invoices, that is $90,000 walking out the door each year. Furthermore, vendors constantly send duplicate invoices when their payment is two days late—some change the invoice number from INV-1001 to INV-1001A. No invoice with any duplicate suspicion or price variance over 2% can ever be auto-approved, period."*
   >
   > *(Contradiction: Demands micro-level oversight and strict tolerances that make 95% straight-through processing mathematically impossible).*

3. **Sarah Jenkins (Senior Accounts Payable [AP] Clerk):**
   > *"Software always fails on real-world invoices. Half of our suppliers don't even put our Purchase Order (PO) number on the bill—they put the sales order number or the requisition name of our warehouse supervisor. And when freight is added as an extra line item, is the computer going to reject the whole shipment? I spend two hours every morning just hunting down warehouse Goods Receipt (GR) slips."*
   >
   > *(Contradiction: Expresses deep skepticism of Artificial Intelligence [AI] extraction, yet highlights the exact manual bottleneck that makes an automated exception assistant necessary).*

4. **Elena Rostova (Lead Information Technology [IT] Admin):**
   > *"You cannot have direct Structured Query Language (SQL) access to our legacy Enterprise Resource Planning (ERP) database. It's a 22-year-old schema with custom triggers that deadlock if you do bulk inserts. Any integration must go through our legacy Representational State Transfer (REST) API wrapper, which occasionally returns 503 Service Unavailable errors and requires idempotency tokens. Also, untrusted Portable Document Format (PDF) files from random supplier emails represent a prompt injection and malware surface."*
   >
   > *(Constraint: Hard architectural boundary—must interact via a flaky REST API and treat all invoice input as adversarial).*

5. **Marcus Vance (Junior Accounts Payable [AP] Clerk):**
   > *"I don't mind the computer doing the matching, but please don't make me use another complicated tool. If I have to open five windows to compare an invoice Portable Document Format (PDF) against the Purchase Order (PO) and Goods Receipt (GR), I'd rather just keep using my dual-monitor Excel sheet."*
   >
   > *(Design requirement: Review User Interface [UI] must present side-by-side visual diffs and allow one-click action within 60 seconds).*

---

## 4. Current-State Process Flow

```
[Supplier Invoice (PDF/Email)]
               │
               ▼
[Step 1: Mailbox Triaging] ── (3-5 min/invoice)
   • Accounts Payable (AP) Clerk downloads attachment, verifies readability, tags vendor.
               │
               ▼
[Step 2: Legacy ERP Lookup] ── (5-8 min/invoice)
   • Clerk queries Enterprise Resource Planning (ERP) for Purchase Order (PO) number by supplier name or Stock Keeping Unit (SKU) lookup.
   • Clerk retrieves dock Goods Receipt (GR) notes.
               │
               ▼
[Step 3: Manual 3-Way Reconciliation] ── (8-12 min/invoice)
   • Compares: Invoice Line Items vs. Purchase Order (PO) Price vs. Dock Received Goods Receipt (GR) Quantity.
   • Matches cleanly (~78%) ──► Manual data entry into ERP ──► Approved for payment.
   • Mismatches (~22%) ──────► Escalated to Exception Pile.
               │
               ▼
[Step 4: Exception Resolution] ── (2-5 days turnaround)
   • Clerk emails warehouse manager (quantity check) or buyer (price variance).
   • Invoices sit in inbox queues; month-end close accumulates 300+ unresolved items.
```

**Total Clerk Time per Invoice:** 16 to 25 minutes for clean invoices; days for exceptions.

---

## 5. Pain Points (Ranked by Financial & Operational Impact)

| Rank | Pain Point | Frequency | Time / Cost Impact | Root Cause |
|---|---|---|---|---|
| **1** | **Month-End Close Overrun** | Monthly (every close cycle) | 4-6 days overtime for entire accounting team (~$65k/yr in overtime). | ~400 mismatched invoices pile up until closing week, requiring frantic reconciliation. |
| **2** | **Lost Early-Payment Discounts** | ~15% of all eligible invoices | Estimated $110,000 lost annual cash discounts (2% discount within 10 days [2/10 Net 30]). | Processing latency (12-16 days average) exceeds vendor 10-day discount windows. |
| **3** | **Duplicate & Erroneous Invoices** | ~3% exact duplicates, ~2% near-duplicates | Estimated $45,000 in annual erroneous payouts and recovery audits. | Vendors re-sending invoices with amended suffixes (`-A`, `-REV`) when payment is delayed. |
| **4** | **Unmatched / Missing Purchase Orders (POs)** | ~2% of monthly volume (~36 inv/mo) | 3-5 days holding time per invoice; friction with purchasing team. | Vendor omission or buyers placing phone orders without creating Enterprise Resource Planning (ERP) Purchase Order (PO) headers. |
| **5** | **Line-Item Price & Quantity Variances** | ~8% of volume (~144 inv/mo) | 15-20 clerk hours/week spent on email back-and-forth. | Freight additions, fuel surcharges, partial shipments, and mid-contract vendor price hikes. |

---

## 6. Success Metrics

| Metric | Baseline (Today) | Pilot Target (Week 6) |
|---|---|---|
| **Extraction Field Accuracy** | N/A (100% manual entry without Optical Character Recognition [OCR]) | **$\ge$ 95%** across all fields |
| **Match / Exception Classification Accuracy** | 91% (human error rate ~9%) | **$\ge$ 98%** deterministic accuracy |
| **Agent Action Accuracy on Exceptions** | 0% (all manual) | **$\ge$ 85%** on exception reasoning |
| **Auto-Resolution Rate** | 0% | **60% to 70%** (Clean match + allowed low-risk) |
| **False Auto-Approval Rate** | ~1.5% undetected human error | **$< 1\%$ (Hard Zero-Tolerance Guardrail)** |
| **Average Invoice Processing Time** | 18 minutes | **$<$ 60 seconds** human touch on exceptions |
| **Adversarial / Prompt-Injection Defense** | 0 tests | **10 / 10** adversarial cases blocked |

---

## 7. Constraints & Guardrails

1. **Security & Prompt Injection:** All invoice Portable Document Format (PDF) and email contents must be treated as untrusted data. No tool execution or Enterprise Resource Planning (ERP) writeback may be triggered purely by model interpretation of invoice text.
2. **Deterministic Matching Invariant:** Invoice line item comparisons against Purchase Order (PO) and Goods Receipt (GR) records must be strictly deterministic code (zero Large Language Model [LLM] involvement). The Large Language Model (LLM) is restricted to extraction, fuzzy vendor tiebreaking, and exception reasoning.
3. **Hardened Safety Boundaries:**
   - No invoice exceeding **$2,500.00** may ever be auto-approved without human clerk review.
   - Any invoice flagged with duplicate suspicion (exact or near-duplicate) is hard-locked from auto-approval.
   - Auto-resolution is restricted to an explicit allow-list of low-risk exception types with agent confidence $\ge 0.85$.
4. **ERP Interface Limitations:** No direct database connections. All integrations must interact through the simulated legacy Representational State Transfer (REST) Application Programming Interface (API) (`/po`, `/receipts`, `/approve`, `/hold`) tolerating 503 Service Unavailable retries and requiring idempotency tokens.

---

## 8. Risks and Mitigations

| Risk | Category | Impact | Mitigation Strategy |
|---|---|---|---|
| **Vendor Template Drift** | Technical | Extraction degradation on new invoice formats. | Multi-tier vendor resolution; fallback to "needs human extraction" on low confidence; active evaluation (eval) monitoring. |
| **Hallucinated Approvals** | Operational | Erroneous payment of incorrect totals. | Code-level policy layer outside Large Language Model (LLM) enforces approval thresholds and tolerance limits. |
| **Clerk Mistrust & Pushback** | Organizational | Clerks reject automated suggestions and redo work. | Highlighting exact visual differences in side-by-side User Interface (UI); full audit trail showing reasoning and evidence. |
| **ERP Availability & Concurrency** | Architectural | Writebacks fail during Enterprise Resource Planning (ERP) 503 bursts or slow responses. | Exponential backoff retry loop with unique idempotency keys per transaction. |
| **Adversarial Invoices** | Security | Prompt injection modifying payment routing or terms. | Strict delimiter parsing, untrusted text isolation, and refusal of directive instructions inside invoices. |

---

## 9. Out of Scope for Engagement

To maintain ruthless scope discipline within the 6-week Forward Deployed Engineer (FDE) deployment, the following are explicitly **out of scope**:
- Direct Electronic Funds Transfer (EFT), Automated Clearing House (ACH), or automated check printing (Enterprise Resource Planning [ERP] handles payment runs).
- Multi-currency Foreign Exchange (Forex) hedging or dynamic treasury management (handled in United States Dollar [USD] and Canadian Dollar [CAD] base rates).
- Real-time chat integrations (Slack, Microsoft Teams bot approvals).
- Multi-tenant enterprise Role-Based Access Control (RBAC) beyond Clerk and Manager roles.
- Direct database schema alterations to the customer's legacy Enterprise Resource Planning (ERP) database.

---

## 10. Proposed Technical Approach & Rollout Strategy

### Technical Architecture
The solution deploys a layered pipeline:
1. **Intake Service:** Receives Portable Document Format (PDF) attachments and email streams, generates Secure Hash Algorithm 256-bit (SHA-256) document hashes, and stores immutable raw files.
2. **Extraction & Normalization:** Employs Google Gemini with strict Pydantic structured output schemas, normalizes dates/currencies, and executes tiered vendor resolution (exact $\rightarrow$ Rapid Fuzzy String Matching [RapidFuzz] $\rightarrow$ Large Language Model [LLM] tiebreak).
3. **Deterministic Matcher:** Executes 2-way and 3-way line-item reconciliation against Enterprise Resource Planning (ERP) Purchase Orders (POs) and Goods Receipts (GRs) with configurable mathematical tolerances ($\pm 2\%$ price, exact quantity).
4. **Google Agent Development Kit (ADK) Exception Agent:** Engaged exclusively when matching generates a typed exception (`PRICE_VARIANCE`, `QTY_MISMATCH`, etc.). Uses typed tools (`lookup_po`, `lookup_receipt`, `get_vendor_history`) to assemble evidence and propose structured resolutions.
5. **Hardened Policy Layer:** Enforces deterministic business boundaries (dollar caps, duplicate bans) before any writeback.
6. **Next.js Review User Interface (UI):** Surfaces flagged exceptions to Accounts Payable (AP) clerks with side-by-side visual diffs and one-click actions.

### Phased Rollout Plan
```
[Weeks 1-2: Shadow Mode]
   • Agent processes all invoices in parallel with human clerks.
   • Zero Enterprise Resource Planning (ERP) writebacks. Agent outputs recommendations to shadow log for evaluation.
   • Gate: Verify false auto-approval rate is 0.0% across 500 shadow invoices.

[Weeks 3-4: Assisted Mode (Clerk-in-the-Loop)]
   • Clean matches automatically hold in review queue with pre-populated approvals.
   • Exception recommendations displayed to clerks in review User Interface (UI).
   • Clerk retains 100% final approval authority.
   • Gate: Measure clerk processing time drops below 60 seconds per exception.

[Weeks 5-6: Guarded Automation Pilot]
   • Clean matches auto-post directly to Enterprise Resource Planning (ERP).
   • Low-risk exceptions (< $500, price variance < 1%) auto-resolve under strict policy gates.
   • High-dollar, duplicate, and ambiguous cases route to clerk User Interface (UI) with full audit logging.
```
