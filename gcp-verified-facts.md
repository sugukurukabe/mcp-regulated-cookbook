---
title: "GCP Verified Facts — Sugukuru Inc. MCP Fleet"
status: living
version: 0.4.0
last_reviewed: 2026-04-28
maintainer: "@sugukurukabe"
verification_window: "Cloud Run console snapshot 2026-04-28; GCP Billing April 2026 MTD through 2026-04-26"
license: "Apache-2.0; this file is the truth ledger for cookbook-published claims about Sugukuru's deployment."
---

# GCP Verified Facts — Sugukuru Inc. MCP Fleet

> **Purpose.** This file is the **truth ledger** for any cookbook chapter, case study, or tool output that makes a factual claim about Sugukuru's deployment. Per `OPERATIONS.md` Section C.1, this file sits at precedence level 6 — above past Claude session output, above project memos, above human recollection, but below live GCP state. When in doubt, re-verify against live state and update this file.
>
> **Verification window.** Every fact below is anchored to a specific source observable on or before 2026-04-28. Facts older than 90 days SHOULD be re-anchored per OPERATIONS.md D.3.
>
> **Out of scope.** This file documents the `sugukuru` GCP project only. Sugukuru's `suguvisa-mcp` (a separate TypeScript MCP server in a separate GCP project, anticipated to be split into a separate company in mid-2026) is intentionally not documented here. It will become Case Study #02 at the appropriate time.

---

## 1.0 Project identification

The Sugukuru MCP fleet is deployed in a single GCP project:

| Field | Value |
|---|---|
| GCP Project ID | `sugukurucorpsite` |
| GCP Project Display Name | Sugukuru |
| Organization | sugu-kuru.co.jp |
| Primary Region | asia-northeast1 |
| Deployment first verified | 2026-03-22 (`sugukuru-core` initial Cloud Run revision) |

This project ID is published explicitly because the Operator Experience section in Case Study #01 cites GCP API surface metrics (Google Drive, Cloud Build, Document AI, etc.) that are scoped to this project. Readers verifying the cookbook's claims against gcloud or GCP Console outputs need to know which project to query. The project ID is not a credential; access controls live in IAM, not in the project ID.

The operator's separate `suguvisa-mcp` project lives in a different GCP project (out of scope for this case study; see project README) and uses a separate set of metrics.

## 1. MCP fleet composition

### 1.1 Confirmed MCP servers

| Service | Role | First deployed | Runtime | Verified via |
|---|---|---|---|---|
| `sugukuru-core` | HR, visa cases, document generation, Document AI integration | 2026-03-22 | Python 3.12 + FastMCP | Cloud Run revision creation timestamp; codebase inspection (`aios` Python codebase) |
| `sugukuru-finance` | freee + GMO Aozora Net Bank integration | 2026-03-22 | Python 3.12 + FastMCP | Cloud Run revision creation timestamp; codebase inspection |
| `sugukuru-crm` | Sales pipeline, dispatch destinations | 2026-03-22 | Python 3.12 + FastMCP | Cloud Run revision creation timestamp; codebase inspection |

### 1.2 Confirmed non-MCP supporting services

| Service | Role | Why it is not an MCP server |
|---|---|---|
| `sugukuru-hub` | REST API integration hub holding 33 env vars including `VERTEX_AI_SEARCH_SERVING_CONFIG`, freee tokens, GMO Bank credentials, Slack, SmartHR, Supabase | YAML has no `sessionAffinity`, env vars indicate REST patterns, served as conventional HTTP endpoints to the MCP fleet |
| `sugukuru-comms` | WhatsApp Business API webhook receiver | Currently a vanilla Node.js Express app routing inbound WhatsApp messages. **Future MCP migration is planned** (the multi-agent orchestration described in earlier internal memos is the planned future state, not the current state). Until that migration occurs, it is not an MCP server and contains no MCP tools. |

### 1.3 Confirmed exclusions

| Service | Why excluded from cookbook |
|---|---|
| `sugukuru-mcp` | Personal experimental service deployed by a team member; only 2 revisions, max-instances 2; not part of production fleet |

### 1.4 Cookbook publishing convention for fleet count

The cookbook documents Sugukuru's fleet as: **"three MCP servers (`sugukuru-core`, `sugukuru-finance`, `sugukuru-crm`), one supporting REST API (`sugukuru-hub`), and one webhook receiver (`sugukuru-comms`) whose MCP migration is planned but not yet implemented."**

The cookbook MUST NOT describe the fleet as "four MCP servers" — that would aggregate `sugukuru-comms` into the MCP count incorrectly. The cookbook MAY describe the fleet as "three live MCP servers plus supporting services" for brevity.

---

## 2. Cloud Run configuration

### 2.1 Per-service scaling (verified via GCP Console 2026-04-28)

| Service | min-instances | max-instances (revision) | max-instances (service) | sessionAffinity | startup-cpu-boost | timeoutSeconds |
|---|---|---|---|---|---|---|
| `sugukuru-core` | **1** | 10 | 20 | **`"true"`** | `"true"` | 300 |
| `sugukuru-finance` | 0 | 10 | 20 | **`"true"`** | _(not yet verified)_ | 300 |
| `sugukuru-crm` | 0 | 10 | 20 | **`"true"`** | _(not yet verified)_ | 300 |
| `sugukuru-hub` (REST) | 0 | 10 | 20 | not set | _(not yet verified)_ | 300 |
| `sugukuru-comms` (webhook) | _(not separately verified)_ | _(not separately verified)_ | _(not separately verified)_ | _(not applicable — not stateful MCP)_ | _(not separately verified)_ | _(not separately verified)_ |

### 2.2 Container concurrency

All MCP services: **`containerConcurrency: 80`** (initial revision through current; verified 2026-04-28).

### 2.3 Region and networking

- All services: `asia-northeast1`.
- VPC connector: **none** (Networking tab confirms).
- Service Mesh: **none**.
- Ingress: **All** (direct internet exposure).

### 2.4 Static egress IPs

- Production: `34.84.81.176`
- Development: `34.85.56.97`

These are reserved for GMO Aozora Net Bank API allowlisting and are publishable in the cookbook.

### 2.5 Notable revision history facts

- **No "Path A → Path B" migration occurred.** The current scaling and `sessionAffinity` configuration was set at initial deployment per `deploy-mcp-split.sh` (with subsequent manual adjustments — see §2.6).
- **Initial deploy script** (`deploy-mcp-split.sh` lines 78–92) sets `--min-instances=0 --max-instances=10` for all services. Production has diverged: `core` was manually adjusted to `min-instances: 1`, and all services were raised to `max-instances: 20`.

### 2.6 Manual adjustments after initial deployment

- `sugukuru-core`: raised `min-instances` from 0 → 1 (date and trigger pending verification; the change is the practical realization of Pattern 01 Path A).
- All services: raised `max-instances` (service-level) from 10 → 20.

---

## 3. Codebase

### 3.1 Source tree organization

The Sugukuru MCP fleet's source code lives in a single Python monorepo internally named **`aios`** (located at `~/aios` on the operator's development machine). When the cookbook needs to reference this codebase by name, the convention is **"the `sugukuru-core` Python codebase (internally named `aios`)"** — naming the user-facing service first, with the internal name in parentheses for readers who may encounter it in subsequent code references.

The `aios` monorepo contains the source for `sugukuru-core`, `sugukuru-finance`, `sugukuru-crm`, and `sugukuru-hub`. It does **not** contain `sugukuru-comms` (separate Node.js project) or `suguvisa-mcp` (separate TypeScript project, separate GCP project — out of scope for this cookbook).

### 3.2 Tool count

**115 unique MCP tool definitions** are registered across the three MCP servers (`sugukuru-core`, `sugukuru-finance`, `sugukuru-crm`), per direct codebase inspection on 2026-04-28. (Earlier drafts stated 117; this was corrected via re-verification — see `memo-errata.md` §3.)

The 115 tools are spread across the three servers; per-server counts are not separately recorded here, as the cookbook treats the fleet as a single tool surface for annotation-discipline purposes.

### 3.3 Spec version targeted

MCP spec **2025-11-25** is the version the cookbook documents and Sugukuru's fleet is assumed to conform to. SDK upgrades that move the target spec version will trigger a knowledge-update procedure (OPERATIONS.md D.1).

---

## 4. Session continuity mechanism

### 4.1 Verified mechanism

Sugukuru's MCP fleet uses **Cloud Run-native sticky sessions with `sessionAffinity: "true"`** plus a **per-service warm-baseline strategy** (`sugukuru-core` at `min-instances: 1`, others at 0). This is Pattern 01 Path A for `core` and Pattern 01 Path B for `finance`/`crm`.

### 4.2 Verified absence of external session store

- **Memorystore for Redis**: instance does not exist in this project. `redis.googleapis.com` API is unenabled (Enable button visible).
- **Memorystore (Valkey)**: `memorystore.googleapis.com` API is unenabled.
- **Redis environment variables**: no `REDIS_*` env vars on any service.
- **GCP Billing through 2026-04-26**: no Memorystore line item.

The cookbook MUST NOT claim Sugukuru uses an external session store. See `memo-errata.md` §1 for the false claim that prompted this verification.

### 4.3 Cloud SQL

A Cloud SQL instance exists (~¥3,400 / month, April 2026 partial). It is not used for MCP session state per stdout log inspection (no session_id log entries traceable to Cloud SQL queries). Its role is instead operational metadata storage for non-MCP backend functions. The cookbook does not currently make claims about it.

### 4.4 Observed session reconnection pattern

From `sugukuru-core` Cloud Logging (verified excerpt, 2026-04-27 night):

```
23:46 GET /mcp  → 23:48 POST /mcp
23:51 GET /mcp  → 23:54 POST /mcp
23:56 GET /mcp  → 23:59 POST /mcp
00:01 GET /mcp  → 00:05 POST /mcp
00:07 GET /mcp  → 00:10 POST /mcp     [GET disconnected at 301 seconds]
00:12 GET /mcp  → 00:15 POST /mcp
```

All from the same IP `114.142.108.71` with `userAgent: "Cursor/3.2.11 (darwin arm64)"`. The 5-minute reconnect cadence is consistent with `timeoutSeconds: 300` plus client-side automatic re-establishment. Across all reconnects the session continued operating, consistent with `sessionAffinity` cookie pinning the reconnect to the same instance.

This excerpt is the live-deployment evidence supporting Pattern 01 Path A's claim that the affinity-cookie-plus-warm-baseline configuration survives Cloud Run's 300-second GET timeout without external session storage.

---

## 5. Database (Supabase)

### 5.1 Instance

- Project name: `sugukuru_ai_os`
- Region: `ap-southeast-1` (Singapore)
- Plan: **Supabase Micro** (`t4g.micro`)
- Last migration: `production_master_cleanup_20260425`

### 5.2 Operational metrics (verified 2026-04-28, 7-day rolling window)

| Metric | Value |
|---|---|
| Total Requests | 74,789 |
| Database Requests | 65,666 (~9,380/day) |
| Auth Requests | 8,700 (~1,243/day) |
| Active DB connections | 9 / 60 |
| CPU utilization | 1% |
| Disk utilization | 11% |
| RAM utilization | 50% |

### 5.3 Multi-tenancy posture

The Supabase instance hosts **62 tenant-isolated tables** with PostgreSQL Row-Level Security (RLS) enforcing org-scoped access. This is the operational substrate for [Pattern 04: Multi-tenant MCP Architectures](docs/patterns/04-multi-tenant-mcp.md).

Pilot tenants in live operation: `sugukuru` (HQ-internal), `ja-kimotsuki` (agricultural cooperative), `win-international` (dispatch destination).

### 5.4 Cost

Supabase Micro plan: **~$25 USD / month**.

---

## 6. Observed Cloud Run metrics (last 30 days, ending 2026-04-28)

### 6.1 Container startup latency

| Service | p50 | p99 |
|---|---|---|
| `sugukuru-core` | ~5s | ~30s |
| `sugukuru-finance` | ~5s | ~10s |
| `sugukuru-crm` | ~5s | ~10s |

### 6.2 Peak concurrent instances

| Service | Observed peak |
|---|---|
| `sugukuru-core` | ~10–20 (range observed; `max-instances: 20` is the ceiling) |
| `sugukuru-finance` | ~4 |
| `sugukuru-crm` | ~4 |

### 6.3 Sustained request rate

| Service | Sustained request rate |
|---|---|
| `sugukuru-core` | ~0.05–0.1 req/s |
| `sugukuru-finance` | ~0.05 req/s peak |
| `sugukuru-crm` | ~0.05 req/s peak |

### 6.4 Limits of measurement

The application layer does not yet emit OpenTelemetry metrics. Per-tool latency, p50/p99 in milliseconds, and concurrent MCP session counts (as opposed to Cloud Run instance counts) are **not directly measured** as of 2026-04-28. Cookbook claims about these metrics MUST use phrases such as "inferred from related metrics" or "not directly measured."

---

## 7. Cost (verified via GCP Billing console)

### 7.1 April 2026 MTD (Apr 1–26, 26 days, partial month)

| Line item | Subtotal (¥) | Notes |
|---|---|---|
| Cloud Run | 25,390 | All services combined |
| Container Registry vulnerability scanning | 7,233 | |
| Compute Engine | 4,875 | |
| Cloud SQL | 3,401 | See §4.3 |
| Secret Manager | 3,282 | |
| Gemini API | 2,787 | +1569% MoM — investigate cause |
| Duet AI | 2,645 | |
| Cloud Document AI API | 1,359 | New this month; aligns with `core`'s `DOCUMENT_AI_ENABLED: true` env var |
| Networking | 778 | |
| Vertex AI Search | 0 | Usage ¥3,025 offset by ¥3,025 free tier credit |
| Other | 510 | |
| **Total (excl. tax)** | **53,260** | |

### 7.2 March 2026 (full month, finalized invoice)

| Line item | Amount (¥) |
|---|---|
| Cloud Run | 13,242 |
| Total (excl. tax) | 34,069 |
| Tax | 3,407 |
| **Invoice total** | **37,476** |

### 7.3 Total infrastructure cost (Cloud Run + Supabase)

For a platform managing 150+ active foreign workers' PII, visa statuses, and financial records with 115 MCP tools and multi-tenant isolation:

- **Cloud Run** (3 MCP servers + hub + comms): ~¥25,400 / month (~$162 USD)
- **Supabase** (Micro plan): ~$25 USD / month
- **Estimated total**: ~$187 USD / month

### 7.4 Cookbook-publishable cost framings

The cookbook MAY publish:

- "Cloud Run subtotal: ~¥25,390 / month (April 2026 partial-month MTD)"
- "Total project running cost: ~¥53,260 / month (April 2026 MTD)" — with caveat that this excludes cumulative cost, third-party API fees outside GCP (freee, GMO), and developer time.
- "Total infrastructure cost (Cloud Run + Supabase): ~$187 USD / month" — with the same caveat.

The cookbook MUST NOT publish:
- Project-lifetime cumulative cost (not measured cleanly enough).
- "Free" or "approximately zero" — neither is true at this scale.

---

## 8. Per-service technology indicators

### 8.1 `sugukuru-core`

- `DOCUMENT_AI_ENABLED: true` — uses Cloud Document AI for OCR.
- Routes specific document types to specialized processors via `DOCUMENT_AI_PROCESSOR_OCR_ID`, `DOCUMENT_AI_PROCESSOR_INVOICE_ID`.
- `DOCUMENT_AI_USE_FALLBACK_GEMINI: true` — falls back to Gemini for unsupported document types.

### 8.2 `sugukuru-hub`

- 33 environment variables observed.
- `VERTEX_AI_SEARCH_SERVING_CONFIG` present — Vertex AI Search is used here.
- Variables consistent with integrations to: freee, GMO Aozora Net Bank, Slack, SmartHR, Supabase, Vertex AI Search.

### 8.3 `sugukuru-finance`, `sugukuru-crm`

Specific env var lists not exhaustively recorded in this file. The `aios` codebase is the source of truth.

### 8.4 `sugukuru-comms`

- Node.js Express webhook receiver for WhatsApp Business API.
- No MCP tool definitions. No `Mcp-Session-Id` handling. Stateless message routing.
- Future MCP migration is planned but not scheduled.

---

## 9. Sugukuru organizational facts (background, not GCP-derived)

These are facts about the deploying organization that the cookbook cites as context. Sourced from operator self-report.

| Fact | Value | Source |
|---|---|---|
| HQ headcount | under 30 | operator |
| Workers managed in past 3 years (cumulative) | 300+ | operator |
| Steady-state active workers under MCP-driven case management | **150+** | operator |
| Total worker records in Supabase `staff` table | 400+ | Supabase dashboard, includes historical and inactive records |
| Region | Kagoshima, Japan | operator |
| Industry | Specified Skilled Worker / 特定技能 visa-based agricultural worker dispatch | operator |
| Applicable laws cited in cookbook | Immigration Control Act, Worker Dispatch Law, APPI | operator |

The active-worker number that cookbook chapters use is **150+**. The 400+ figure is the all-time `staff` table record count and SHOULD only appear when explicitly framed as the total record count, not as the active worker base.

---

## 10. Document maintenance

### 10.1 Update triggers

Per `OPERATIONS.md` D.1, this file MUST be updated when:
- A new GCP configuration is observed.
- A new service is added or retired.
- A new MCP spec version is adopted.
- A discrepancy is found per OPERATIONS.md C.3.
- `sugukuru-comms` migrates to MCP — at which point §1.1 expands to four MCP servers.

### 10.2 Quarterly re-anchor

Per OPERATIONS.md D.3, sample at minimum 5 facts per quarter and re-verify against current GCP state. Next due: 2026-07-28.

## 11. Changelog

- **0.4.0** (2026-04-28): added §1.0 explicit GCP project identification (`sugukurucorpsite`); cross-referenced from new Operator Experience section in Case Study #01 and from memo-errata §13.4

- **0.3.0** (2026-04-28) — Major reconciliation against Antigravity-validated codebase inspection. Resolved all `[PENDING]` items from v0.2.0: runtime confirmed as Python 3.12 + FastMCP across all three MCP servers; `sugukuru-comms` confirmed as Express webhook (not an MCP server), with future MCP migration noted. Added §3 (codebase) introducing the `aios` monorepo naming convention. Added §5 (Supabase) with operational metrics and multi-tenancy posture. Added §6 cost framings. Tool count corrected from 117 (earlier draft) to 115 per re-verification.
- **0.2.0** (2026-04-28) — Reconciliation against Antigravity v0.3.1 of Pattern 01. Pre-codebase-inspection state.
- **0.1.0** (2026-04-28) — Initial truth ledger.
