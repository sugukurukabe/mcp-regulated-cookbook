---
title: "Sugukuru Inc.: Three Python MCP servers and a WhatsApp webhook for Japanese SSW visa and labor dispatch operations"
attribution: attributed
status: published
last_reviewed: 2026-04-27
patterns_validated:
  - 01-cloud-run-multi-instance
  - 04-multi-tenant-mcp
contributors:
  - "@sugukurukabe (Sugukuru Inc., CEO/CTO)"
license: "Apache-2.0; case study text additionally attributable to Sugukuru Inc."
---

# Case Study 01: Sugukuru Inc.

> Three Python FastMCP servers, a REST API hub, and a WhatsApp webhook receiver on Cloud Run `asia-northeast1`, in production since March 2026, supporting visa, finance, and CRM operations for 400+ foreign workers under the Japanese Immigration Control Act.

## At a glance

| | |
|---|---|
| Organization | Sugukuru Inc., Kagoshima, Japan |
| Industry | Agricultural worker dispatch (Specified Skilled Worker / 特定技能) |
| MCP servers in production | 3 (`sugukuru-core`, `sugukuru-finance`, `sugukuru-crm`) |
| Supporting services | 2 (`sugukuru-hub` REST API, `sugukuru-comms` webhook) |
| Platform | Google Cloud Run, region `asia-northeast1` |
| Runtime | Python 3.12 (MCP servers) / Node.js (comms) |
| MCP transport | `streamable_http` (stateful) |
| Session continuity strategy | Pattern 01 — Hybrid: Path A (warm baseline, Min: 1) for `core`, Path B (scale-to-zero, Min: 0) for `finance`/`crm`. Cloud Run-native sticky sessions. No external session store. |
| Production start dates | `core`/`finance`/`crm`: 2026-03-22 |

## What we run and why

Sugukuru is a small operator in a regulatory-dense vertical. The active worker population — whose visa cases, dispatch contracts, and payroll records are managed through MCP-driven operations — exceeds **400 individuals** (verified from the Supabase `staff` table, April 2026).

The MCP fleet is split across three Python `FastMCP` servers, supported by a REST API hub and a Node.js WhatsApp webhook:

- **`sugukuru-core`** (MCP) — HR records, visa cases, document generation. 
- **`sugukuru-finance`** (MCP) — Integrations with freee and GMO Aozora Net Bank. Separated because the auth boundary and audit requirements are different.
- **`sugukuru-crm`** (MCP) — Sales pipeline, client records, dispatch destination management. 
- **`sugukuru-hub`** (REST API) — An integration surface containing internal integrations with external tools.
- **`sugukuru-comms`** (Webhook) — A vanilla Express app acting as a WhatsApp Business API webhook receiver. Unlike previous documentation drafts, this is *not* an MCP server and contains no MCP tools. It strictly routes incoming messages.

## Cloud Run configuration as of April 2026

All Python MCP services run on Cloud Run in `asia-northeast1` with `containerConcurrency: 80`. 

Scaling configurations:

| Service | min instances | max instances | sessionAffinity | Runtime |
|---|---|---|---|---|
| `sugukuru-core` (MCP) | **1** | 20 | true | Python 3.12 |
| `sugukuru-finance` (MCP) | 0 | 20 | true | Python 3.12 |
| `sugukuru-crm` (MCP) | 0 | 20 | true | Python 3.12 |
| `sugukuru-comms` (Webhook) | — | — | unknown | Node.js |

> **Evidence source:** GCP Console Cloud Run Observability tab screenshots, captured 2026-04-28. The initial deploy script (`deploy-mcp-split.sh`) specifies `--min-instances=0 --max-instances=10`, but the actual production values have been tuned post-deployment as shown above.

All MCP servers rely on `--session-affinity`. `core` uses Path A (`min-instances: 1`) for zero cold-start latency as the primary user-facing entry point, while `finance` and `crm` use Path B (`min-instances: 0`) for zero idle cost. This is the production realization of [Pattern 01](../patterns/01-cloud-run-multi-instance.md). The SDK's in-memory session map remains the single source of truth. There is **no Memorystore Redis, no Firestore, no external session store of any kind** in this deployment.

> **Note:** `sugukuru-comms` is deployed separately from the main `deploy-mcp-split.sh` script and its Cloud Run configuration has not been independently verified here.

## What surprised us

**Project memos lie, YAML doesn't.** Our own handoff memos for this project contained several inaccurate technical claims. They claimed we were using TypeScript on Bun (we use Python 3.12 and FastMCP), they claimed `min-instances: 1` was configured for `core` (it is `0`), and they claimed `comms` was an MCP server with `openWorldHint` tools (it is a standard Express webhook with no tools). The discipline of reconciling memos against the codebase and Cloud Run deployment scripts was critical to ensure this cookbook provides actual verified facts.

## Patterns this case study validates

- [Pattern 01: Cloud Run Multi-Instance Session Continuity](../patterns/01-cloud-run-multi-instance.md), v0.3.0 — Hybrid: Path A (warm baseline) for `core`, Path B (scale-to-zero) for `finance`/`crm`. This case study provides production GCP Console evidence for both paths, including container startup latency metrics (p50: ~5s, p99: up to 30s for `core`).
- [Pattern 04: Multi-tenant MCP Architectures](../patterns/04-multi-tenant-mcp.md), v1.0.0 — The `aios` codebase implements ContextVar + automatic `org_id` injection across 62 tenant-isolated tables, with PostgreSQL RLS as defense-in-depth. Pilot tenants (JA Kimotsuki, WIN International) are configured and seeded in production.

## Database infrastructure

All MCP servers connect to a single **Supabase** instance (`sugukuru_ai_os`, MICRO plan) hosted in `ap-southeast-1` (Singapore).

| Metric (7-day window, April 2026) | Value |
|---|---|
| Total Requests | **74,789** |
| Database Requests | **65,666** (~9,380/day) |
| Auth Requests | **8,700** (~1,243/day) |
| Active DB connections | 9 / 60 |
| Resource utilization | CPU 1%, Disk 11%, RAM 50% |
| Last migration | `production_master_cleanup_20260425` |
| Plan | Supabase Micro (`t4g.micro`) |

> **Evidence source:** Supabase Dashboard screenshot, captured 2026-04-28.

Notable: The entire MCP fleet — 115 tools, 400+ worker records, multi-tenant RLS isolation — runs on a **$25/month Supabase Micro instance** with CPU at 1% and RAM at 50%. This is strong evidence that production-grade regulated MCP operations do not require expensive infrastructure.

## Total monthly cost

| Component | Monthly cost (April 2026) |
|---|---|
| **Cloud Run** (3 MCP servers + hub + comms) | ¥25,400 (~$162 USD) |
| **Supabase** (Micro plan) | ~$25 USD |
| **External session store (Redis etc.)** | $0 (not used) |
| **Estimated total** | **~$187 USD/month** |

> **Evidence source:** GCP Billing Reports (April 1–26, 2026). Cloud Run costs include `sugukuru-core` (Min: 1 warm instance), `sugukuru-finance`, `sugukuru-crm` (both Min: 0), `sugukuru-hub`, and `sugukuru-comms`.

For a platform managing 400+ foreign workers' PII, visa statuses, and financial records with 115 MCP tools and multi-tenant isolation, a total infrastructure cost under $200/month demonstrates that enterprise-grade MCP deployments are economically accessible.

## CI/CD pipeline

The companion TypeScript MCP project (`suguvisa-mcp`) runs a GitHub Actions CI pipeline on every push:

- **CI Run #58**: `build-and-test` job — Success, 2m 14s total
- Steps: checkout → pnpm setup → Node.js setup (12s) → Install dependencies (4s) → Build (1m 8s) → Test (36s)
- Triggered by: `on: push` (mandatory for all commits)

> **Evidence source:** GitHub Actions log, `suguvisa-mcp` repository, captured 2026-04-28.

This validates [Pattern 02](../patterns/02-tool-annotation-ci-audit.md)'s approach of enforcing tool annotation compliance through CI.

## Changelog

- **2026-04-27** — First published. Reconciled and corrected numerous architectural inaccuracies from earlier internal memos. Confirmed Python FastMCP stack with scale-to-zero configurations across the board.
