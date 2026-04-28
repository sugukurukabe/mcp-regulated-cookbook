---
title: "Sugukuru Inc.: Three Python MCP servers for Japanese SSW visa and labor dispatch operations"
attribution: attributed
status: published
last_reviewed: 2026-04-28
spec_version: "2025-11-25"
patterns_validated:
  - 01-cloud-run-multi-instance
  - 02-tool-annotations-regulated
  - 04-multi-tenant-mcp
contributors:
  - "@sugukurukabe (Sugukuru Inc., CEO/CTO)"
license: "Apache-2.0; case study text additionally attributable to Sugukuru Inc."
---

# Case Study 01: Sugukuru Inc.

> Three Python FastMCP servers and a REST API hub on Cloud Run `asia-northeast1`, in live operation since early 2026 (`hub` on 2026-02-09, `core`/`crm`/`finance` on 2026-03-22), supporting Sugukuru's own visa, finance, and CRM operations for 150+ active foreign workers under the Japanese Immigration Control Act, Worker Dispatch Law, and APPI. The deployment is internal — Sugukuru runs the MCP fleet for its own business operations rather than selling it as an external product.

## At a glance

| | |
|---|---|
| Organization | Sugukuru Inc., Kagoshima, Japan |
| Industry | Agricultural worker dispatch (Specified Skilled Worker / 特定技能) |
| MCP servers in live operation | 3 (`sugukuru-core`, `sugukuru-finance`, `sugukuru-crm`) |
| Supporting services | 1 REST API hub (`sugukuru-hub`); 1 webhook receiver (`sugukuru-comms`, planned MCP migration) |
| Platform | Google Cloud Run, region `asia-northeast1` |
| Runtime | Python 3.12 + FastMCP |
| MCP transport | `streamable_http` (stateful) |
| Session continuity strategy | Pattern 01 hybrid: Path A for `core` (Min: 1, sticky), Path B for `finance`/`crm` (Min: 0, sticky). No external session store. |
| Multi-tenancy | Pattern 04: ContextVar + automatic `org_id` injection + PostgreSQL RLS across 62 tenant-isolated tables on Supabase |
| Production start | 2026-02-09 (`hub`), 2026-03-22 (`core`/`finance`/`crm`) |
| Operating duration at first publication | ~5 weeks |

## What we run and why

Sugukuru is a small operator (under 30 staff at HQ) in a regulatory-dense vertical. Over the past three years the company has managed dispatch placements for 300+ foreign workers in aggregate; the steady-state active population — workers whose case work is the subject of MCP-driven operations — sits at **150+** at any given time. (The Supabase `staff` table contains 400+ records when historical and inactive workers are included.) Specified-skilled-worker visa operations are subject to the Japanese Immigration Control Act; the dispatch business is subject to the Worker Dispatch Law; communications with foreign-language-native workers in remote agricultural locations are subject to labor-standards requirements that make WhatsApp the practical channel.

The MCP fleet is split across three Python `FastMCP` servers, supported by a REST API hub and a Node.js webhook. The split is by ownership of the underlying system of record:

- **`sugukuru-core`** (MCP) — HR records, visa cases, document generation. Document AI is enabled (`DOCUMENT_AI_ENABLED: true`) with specialized processors for ID cards and invoices, and a Gemini fallback for unsupported document types — see [Pattern 03](../patterns/03-document-ocr-mcp.md).
- **`sugukuru-finance`** (MCP) — Integrations with freee (Japanese accounting SaaS) and GMO Aozora Net Bank. Separated because the auth boundary and audit requirements are different: a finance tool that fires incorrectly can produce a real money movement.
- **`sugukuru-crm`** (MCP) — Sales pipeline, client records, dispatch destination management.
- **`sugukuru-hub`** (REST API, not an MCP server) — An integration surface holding 33 environment variables for external services (freee, GMO Bank, Slack, SmartHR, Supabase, Vertex AI Search, Document AI). Exposed as conventional HTTP endpoints to the MCP fleet and other internal callers. Named here for completeness rather than buried as private infrastructure: the live deployment from which this cookbook draws lessons is genuinely a four-service fleet with one REST hub, and the cookbook's accuracy goals require naming the hub explicitly.
- **`sugukuru-comms`** (webhook receiver, not an MCP server) — A Node.js Express application receiving inbound WhatsApp Business API messages. Currently routes messages to internal handlers without any MCP tools. **A future MCP migration is planned** — the multi-agent orchestration in which a router agent classifies inquiries by topic and dispatches to specialist agents (workplace coordination, safety/labor-standards, daily-life support, learning support, health, emergency escalation) is the planned future state. When that migration occurs, this case study will be revised to include `sugukuru-comms` as the fleet's fourth MCP server and as the live realization of [Pattern 02](../patterns/02-tool-annotations-regulated.md)'s `openWorldHint: true` server-boundary discipline.

**Note:** `sugukuru-hub` and `sugukuru-comms` are managed via separate deployment scripts (not `deploy-mcp-split.sh`). Their Cloud Run configurations are not independently validated here as they are not FastMCP servers.

## Cloud Run configuration as of April 2026

All Python MCP services run on Cloud Run in `asia-northeast1` with `containerConcurrency: 80` and `--vpc-egress=all-traffic` through a Cloud NAT with reserved static IPs (`34.84.81.176` for production, `34.85.56.97` for dev). The static IPs are required for GMO Aozora Net Bank API allowlisting.

| Service | min-instances | max-instances | sessionAffinity | Runtime |
|---|---|---|---|---|
| `sugukuru-core` (MCP) | **1** | 20 | true | Python 3.12 + FastMCP |
| `sugukuru-finance` (MCP) | 0 | 20 | true | Python 3.12 + FastMCP |
| `sugukuru-crm` (MCP) | 0 | 20 | true | Python 3.12 + FastMCP |
| `sugukuru-hub` (REST) | 0 | 10 (rev) / 20 (svc) | not set | Python 3.12 |
| `sugukuru-comms` (webhook) | (separately configured; not relevant to MCP transport) | | not applicable | Node.js |

Evidence: GCP Console Cloud Run Observability tab screenshots, captured 2026-04-28. The initial deploy script (`deploy-mcp-split.sh`) specifies `--min-instances=0 --max-instances=10`; the actual production values diverged after operational tuning, with `core` raised to `min-instances: 1` and all services raised to `max-instances: 20`.

`sugukuru-core` is the only service that runs both `min-instances: 1` and `sessionAffinity: "true"`. This combination is the live realization of [Pattern 01 Path A](../patterns/01-cloud-run-multi-instance.md): a session pins to a warm instance via the affinity cookie, the long-lived MCP `GET /mcp` reconnects every 300 seconds (Cloud Run's request limit) and re-pins to the same instance via the cookie, and the SDK's in-memory session map remains the single source of truth. The other two MCP services run `min-instances: 0` because they tolerate cold starts at session boundary in exchange for zero idle cost — Pattern 01 Path B.

There is **no Memorystore Redis, no Firestore, no external session store of any kind** in this deployment.

## Session state architecture (operational reality, April 2026)

The honest answer to "how do you handle session continuity across multiple Cloud Run instances?" is that we have not had to solve the problem yet. The configuration described above — `sessionAffinity: "true"` plus `min-instances: 1` on `sugukuru-core`, the only MCP server with sustained interactive traffic — is sufficient for our current concurrent-session counts. Cloud Run's session-affinity cookie pins each session to its origin instance, and observed traffic patterns (largely a single human user driving Claude.ai or Cursor against `core`) keep us comfortably inside the affinity guarantee.

This is Pattern 01 Path A for `core` and Path B for the others. It is not Path C (externalized session state via Redis or equivalent). An earlier draft of this case study, derived from a project handoff memo, claimed that Sugukuru had migrated from Path A to Path C using Memorystore Redis after hitting CPU saturation at approximately 12 concurrent sustained sessions. That claim was wrong on multiple counts: there is no Memorystore Redis instance in this deployment, no migration ever occurred, and the claimed concurrent-session threshold was a fabrication of an earlier writing pass. The correction was prompted by direct inspection of the GCP project state — finding `redis.googleapis.com` API in an unenabled state and finding no `REDIS_*` environment variables on any service.

The migration trigger that *would* move us to Path C is identified in [Pattern 01](../patterns/01-cloud-run-multi-instance.md#choosing-between-paths). We have not hit it.

## Multi-tenant data isolation

The Sugukuru fleet processes data for multiple client organizations (pilot tenants currently include `sugukuru` HQ-internal, `ja-kimotsuki`, and `win-international`). Tenant isolation is implemented per [Pattern 04: Multi-tenant MCP Architectures](../patterns/04-multi-tenant-mcp.md): tenant identity is extracted from the API key at the transport phase, stored in a Python `ContextVar`, and automatically injected into all database queries. PostgreSQL Row-Level Security on Supabase provides defense-in-depth at the database layer.

The `aios` codebase implements this for **62 tenant-isolated tables** managing foreign workers' PII, visa statuses, dispatch contracts, and financial records. An LLM agent operating on behalf of one tenant cannot, by design, access another tenant's records — even if the LLM is induced to attempt it.

## Database infrastructure

All MCP servers connect to a single **Supabase** instance (`sugukuru_ai_os`, MICRO plan) hosted in `ap-southeast-1` (Singapore).

| Metric (7-day window, April 2026) | Value |
|---|---|
| Total Requests | 74,789 |
| Database Requests | 65,666 (~9,380/day) |
| Auth Requests | 8,700 (~1,243/day) |
| Active DB connections | 9 / 60 |
| Resource utilization | CPU 1%, Disk 11%, RAM 50% |
| Last migration | `production_master_cleanup_20260425` |
| Plan | Supabase Micro (`t4g.micro`) |

Notable: the entire MCP fleet — 115 tools across three servers, 150+ active worker records (400+ historical), multi-tenant RLS isolation — runs on a **~$25/month Supabase Micro instance** with CPU at 1% and RAM at 50%. This is direct evidence that operational-grade regulated MCP operations do not require expensive infrastructure.

## Total monthly cost

| Component | Monthly cost (April 2026) |
|---|---|
| **Cloud Run** (3 MCP servers + hub + comms) | ¥25,400 (~$162 USD) |
| **Supabase** (Micro plan) | ~$25 USD |
| **External session store (Redis etc.)** | $0 (not used) |
| **Estimated total infrastructure** | **~$187 USD/month** |

For a platform managing 150+ active foreign workers' PII, visa statuses, and financial records with 115 MCP tools and multi-tenant isolation, total infrastructure cost under $200/month indicates that enterprise-grade MCP deployments in regulated domains are economically accessible. This figure excludes third-party API usage (freee, GMO), developer time, and any cumulative project cost. The total project running cost on GCP for April 2026 (including Container Registry vulnerability scanning, Secret Manager, Document AI, Gemini API, networking, and other GCP line items) was approximately ¥53,260.

## What we got right

**Splitting by trust boundary, not by tool count.** The plan to put `comms` in its own MCP server (when its migration occurs) reflects this principle: every tool in `comms` will carry `openWorldHint: true` because every input is untrusted external content. Isolating it as a service-level invariant is more robust than trying to maintain per-tool annotation discipline inside a mixed-trust monolith.

**Static egress IPs from day one.** The cost of provisioning a Cloud NAT and reserved IP is small; the cost of trying to add it under deadline pressure when a banking partner asks for an allowlist is large. Even if you do not need the IPs immediately, having them makes a future "yes" cheap.

**Picking the lightest configuration that works.** We did not start from a textbook architecture diagram and work backwards; we built `sugukuru-core` with a configuration that survived our actual traffic, observed it, and have not yet had reason to change it. Regulated-domain small-to-medium operators do not need Redis to run a stateful MCP server in live operation. The lightest configuration that survives your concurrent-session count is the right default.

**Multi-tenancy from the foundation.** Pattern 04's ContextVar + automatic `org_id` injection + RLS approach was implemented before the first paid tenant onboarded, not retrofitted under tenant pressure. The cost of building tenancy in from day one was small; the cost of retrofitting it on a live single-tenant codebase would have been substantial.

## What surprised us

**Cold starts are longer than we expected.** Pre-deployment estimates were in the 2–4 second range, derived from generic Bun-on-Cloud-Run benchmarks (which we never used; the runtime is Python). Actual cold starts on `sugukuru-core` are 5–20 seconds with a tail to 30 seconds. We have not isolated the dominant contributor — candidates include FastMCP tool-registry construction, Document AI client warm-up, and integration-client initialization. The corollary: `min-instances: 1` on the core server became more important than initially budgeted for.

**Internationalization of tool descriptions is non-trivial.** Tool descriptions are surfaced to the LLM as part of the prompt that selects which tool to call. Translating them naively (Japanese descriptions for Japanese-speaking users) changed model selection behavior in ways we had not predicted, because the descriptions implicitly carry semantic information the LLM uses to disambiguate between similarly-named tools. We currently keep tool descriptions in English regardless of user locale, and translate only the user-facing strings inside `outputSchema` results. This is a topic we expect to revisit as a cookbook pattern in its own right.

**Project memos lie, YAML doesn't.** Our own handoff memos for this project contained several inaccurate technical claims that propagated through multiple Claude sessions before reconciliation. The most consequential were a false claim that we used Memorystore Redis (we don't), a false claim that the runtime was TypeScript on Bun (it's Python on FastMCP — the TS/Bun stack belongs to a separate project), and a false claim that `sugukuru-comms` was already an MCP server (it's a webhook with planned MCP migration). The discipline of reconciling memos against the codebase, `gcloud run services describe` output, and Cloud Run YAML inspection became a project requirement; the cookbook's [`OPERATIONS.md`](../../OPERATIONS.md) and [`memo-errata.md`](../../memo-errata.md) document the operational regime that emerged from these reconciliations.

## What we have not solved

**Audit log schema.** We have audit logs, but the schema has accreted rather than been designed. Reconciling them with the `tools/call` provenance fields a future Pattern 03 (audit log) will recommend is work we have not done.

**Lethal Trifecta defenses.** When `sugukuru-comms` migrates to MCP, it will be the entry point through which untrusted input enters our agent context. We rely today on per-server isolation as the planned defense, but session-taint mechanisms — which would prevent a `comms` session from invoking a `core` tool that has access to another tenant's records — are not yet designed. This is the proposed Lethal Trifecta Defenses pattern and we are watching it.

**Stateless transport readiness.** Path A and B work for our current traffic, but the eventual end state for at least some MCP servers is fully stateless. When the 2026-06 transport spec lands, we expect to evaluate `sugukuru-comms` (post-MCP-migration, where session state is least valuable) for stateless first.

**Per-tool latency measurement.** The application layer does not yet emit OpenTelemetry metrics. Per-tool p50/p99 latency is not directly measured. A future revision of this case study will add per-tool latency once an OpenTelemetry collector is deployed.

## Patterns this case study validates

- [Pattern 01: Cloud Run Multi-Instance Session Continuity](../patterns/01-cloud-run-multi-instance.md) — Path A for `core`, Path B for `finance`/`crm`. Production GCP Console evidence including container startup latency, sticky-session reconnect logs, and the absence of an external session store.
- [Pattern 02: Tool Annotations for Regulated Operations](../patterns/02-tool-annotations-regulated.md) — Tool annotations across the fleet have been assigned with awareness of Japanese Immigration Control Act and Worker Dispatch Law constraints from project inception. A formal documented annotation review against specific statutory provisions has not yet been published; Pattern 02 represents the framework that future review will follow.
- [Pattern 04: Multi-tenant MCP Architectures](../patterns/04-multi-tenant-mcp.md) — ContextVar + automatic `org_id` injection + PostgreSQL RLS on Supabase, applied across 62 tenant-isolated tables. Pilot tenants in live operation.

## Numbers

Concrete numbers, with their sources and limitations stated.

| Metric | Value | Source / caveat |
|---|---|---|
| Production start | 2026-02-09 (`hub`), 2026-03-22 (`core`/`finance`/`crm`) | Cloud Run revision creation timestamps |
| Operating duration at first publication | ~5 weeks | Same |
| MCP servers in live operation | 3 | Direct enumeration |
| MCP tools registered | 115 | `aios` codebase inspection, commit `a0ab310` (corrected from earlier 117 figure) |
| Active workers under MCP-driven case management | 150+ | Operator self-report; this is the meaningful business metric |
| Records in Supabase `staff` table | 400+ | Supabase dashboard; includes historical/inactive workers |
| Tenant-isolated tables | 62 | `aios` codebase / Supabase schema |
| Pilot tenants in live operation | 3 | `sugukuru`, `ja-kimotsuki`, `win-international` |
| Cold start range, `sugukuru-core` | 5–20s typical, p99 to ~30s | Cloud Run "container startup latency" metric |
| Concurrent MCP sessions, observed peak | small single digits, typically 1 | Inferred from `sugukuru-core` peak instance count |
| Cloud Run cost | ~¥25,390 / month (April 2026 MTD) | GCP Billing console |
| Total GCP cost | ~¥53,260 / month (April 2026 MTD) | GCP Billing console; excludes third-party APIs |
| Supabase cost | ~$25 USD / month | Supabase plan (Micro) |
| Total infrastructure cost | ~$187 USD / month | Cloud Run + Supabase only; excludes third-party API fees, developer time, project-lifetime cumulative |
| External session store latency | not applicable | No external session store deployed |
| MCP-layer outages traceable to fleet issues | none recorded in 5 weeks | Audited only to the extent of routine error monitoring; no formal SLA |

## Changelog

- **2026-04-28** — First published. Reconciled all factual claims against the `aios` codebase, GCP Console state, Supabase dashboard, and GCP Billing console before publication. Validates Patterns 01, 02, and 04. The pre-publication drafting included substantial corrections; see [`memo-errata.md`](../../memo-errata.md) for the record.
