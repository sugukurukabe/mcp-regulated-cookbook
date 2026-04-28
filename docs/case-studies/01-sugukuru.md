---
title: "Sugukuru Inc.: Three Python MCP servers for Japanese SSW visa and labor dispatch operations"
attribution: attributed
status: published
version: 0.2.0
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

## Operator Experience: How a four-person team drives 115 tools through an IDE

This section documents how Sugukuru's MCP fleet is actually used day-to-day. It is included because the operational pattern — a 100+ worker dispatch operation running its administrative work primarily through Cursor and Antigravity rather than purpose-built admin UIs — diverges significantly from the conventional "build an admin dashboard, then use it" pattern that most operators default to. Whether this pattern generalizes is an open question; what follows is what works for one team at one scale, with usage instrumentation supplied to back the claims.

### The team: there are no "admin staff" here

Sugukuru's back-office is run by **four people who all use Cursor and Antigravity daily as their primary work interface.** Internally the team has retired the concept of an "administrative staff member" — a category that, in conventional organizations, refers to people who execute structured tasks against admin dashboards. Instead the team uses the role term "**AI administrator**" (AI 管理者), reflecting the actual job: managing AI agents that perform the structured tasks, rather than performing them by hand against a dashboard.

The CEO/CTO is the heaviest user (and authors most of the tools described below). Among the other three back-office members, one team member in their second year at Sugukuru — coming from a non-engineering operations background — has progressed into a tool-authoring role, committing code to the `aios` monorepo alongside the CEO/CTO. The remaining two team members do not currently commit code directly; they drive Cursor sessions for daily back-office work, with their tool-authoring needs surfaced through requests to the two engineers.

This is the cookbook's most consequential operational finding to date: a regulated-domain team can graduate non-engineer members into tool-authoring roles within ~2 years, supported by AI-pair authoring through Cursor and Antigravity. The pattern is not "only engineers can use this stack"; it is "non-engineers can become tool-authors-and-users when the AI authoring partner absorbs the technical knowledge that would otherwise be a barrier."

### Quantified IDE usage (30-day window, 2026-03-30 to 2026-04-28)

The IDE-as-UI claim is backed by direct Cursor team analytics over the 30 days ending 2026-04-28:

| Metric | Value |
|---|---|
| Daily active users (range) | 1–4 |
| Daily active users (average) | 2.1 |
| Days with at least one active user | 29 of 30 |
| Total agent requests | 2,685 |
| Total agent-suggested lines | ~330,000 |
| Total agent-suggested lines accepted | ~284,000 |
| Acceptance rate | ~86% |
| AI-authored line ratio in committed code | **~81%** (81,849 of 101,468 lines added) |
| AI commits in 30 days | 126 |

Some of these numbers warrant explicit framing:

- **The 81% AI-authored ratio** does not mean 81% of code is unreviewed. It means 81% of lines in committed code were originally generated by an AI agent and then accepted by the human reviewer. The ratio measures who *typed first*, not who *decided last*.
- **86% acceptance rate** reflects the operator's working style: drafts are accepted readily because the cycle is fast (regenerate if wrong); the cookbook's quality discipline lives in the production-deploy step rather than the suggestion-accept step. Whether this is the right discipline at scale is open.
- **DAU averaging 2.1** is the team using the IDE during overlapping work sessions, not 2.1 users running concurrently. On the busiest day (2026-04-27) all four team members were active.

The IDE is, in operational terms, the team's primary working surface. Cursor's analytics could be wrong, but they are not generating these numbers from nothing: someone is opening the IDE every day, asking Claude to do work, and accepting the output.

### Code change cadence (verified 2026-04-28 via GitHub compare)

Over the same 30-day window, the `aios` monorepo received **93 commits touching 1,293 files** from 2 git contributors (the CEO/CTO and the 2nd-year team member described above). The 2-contributor count reflects committers, not users — the broader 4-person IDE-driven team includes 2 additional members whose contributions are mediated through AI agents and committed by the 2 git authors.

The cadence — roughly 3 commits per day, sustained across the month — is consistent with the recursive bootstrapping pattern documented further below. Tooling growth is not a quarterly project here; it is part of the ordinary work flow.

### Long-term OAuth integration growth (independent data source)

A third, independent data source corroborates the trajectory above. Sugukuru's Google Workspace admin console — under "Reports → App reports → API control" — exposes a 180-day chart of distinct applications that have been granted OAuth access to the organization's Google services. Over the window 2025-10-28 to 2026-04-26 (the chart's published range), this count grew from approximately **38 to approximately 150 distinct OAuth applications** — a roughly 4× increase across six months, with Drive being the dominant target service.

A note on what this number does and does not represent. This is **not** a count of MCP tools (which is 115, per `gcp-verified-facts.md` §3.2). The OAuth-app count includes any application that the organization has authenticated to Google services via OAuth: Cursor itself, Antigravity, Claude Desktop, individual Cloud Run services that need Drive read access, third-party SaaS integrations, and others. The relationship between OAuth-app count and MCP tool count is not 1:1, and the cookbook does not claim it is.

What the chart does provide is corroborating evidence that *something is growing fast* in Sugukuru's integration surface. The 4× growth across six months in OAuth-granted applications is consistent with — not derivable from, but consistent with — the recursive bootstrapping pattern documented elsewhere in this section. A fully separate measurement system, controlled by Google rather than by the operator, shows the same direction of travel.

The exact composition of those 150 applications is not enumerated in this section. The cookbook expects to revisit this in a future iteration with the breakdown explicit, once a verification pass has cross-referenced the OAuth-app list against the MCP tool inventory and the deployed Cloud Run service list.

### The dual-interface reality

Inside the IDE-primary pattern, the team operates a deliberate split between four interface kinds:

1. **Cursor + Antigravity (the IDE pair)** — the primary back-office interface for over 50% of administrative work. The operator opens the IDE, asks Claude to perform a workflow (compute payroll, reconcile invoices to bank deposits, generate dispatch contracts), and Claude calls the appropriate MCP tools. There is no admin dashboard for these workflows; the IDE chat is the UI.
2. **`sugukuru-os-v4`** — a Next.js application currently in test deployment, serving specific human-in-the-loop approval flows. It is not the primary interface; it is the place where final approval steps live for operations that benefit from a structured form rather than a chat exchange.
3. **External SaaS native UIs** — Slack (~90% via its native UI, ~10% via MCP), WhatsApp (100% via its native interface), and the small remaining portion of legacy SaaS workflows that have not yet been wrapped (~30%). These are channel-native operations where the SaaS's own interface is more efficient than wrapping it in MCP.
4. **Supabase Dashboard** — for ad-hoc database inspection and one-off queries that do not warrant a dedicated tool.

The interesting pattern is not that traditional UIs have been eliminated (they haven't) but that the *primary* interface for the team's daily back-office work is the IDE chat. SaaS UIs are visited for specific channel-native tasks; the IDE is where the day starts and where most of it happens.

### What runs through the IDE (50%+ of administrative work)

The workflows that have moved into the operator-Claude conversation:

- **Worker attendance calculation** across 7+ destination companies, each with their own attendance rules (overtime thresholds, night-shift premiums, paid-leave handling). Pattern 04's tenant-isolated tables hold the per-company rules; the operator says "compute April attendance for [company]" and Claude calls the appropriate tools.
- **Payroll generation (paystubs)** for 150+ active workers monthly. Payroll arithmetic is complex enough that hand-calculation was the prior bottleneck; it is now a single conversation with Claude that yields per-worker paystubs.
- **Invoice ↔ bank deposit reconciliation** ("toh-goh" / 突合 — see below).
- **Hire and exit processing** spanning visa case updates, SmartHR registration changes, freee accounting entries, dispatch contract amendments, and Slack notifications. What used to require touching five SaaS UIs in sequence is now a single tool-chained call from a single conversation.
- **Document generation with Claude integration** — dispatch contracts, employment verification letters, and regulatory submissions, including macro-heavy Excel templates required by Japan's Immigration Services Agency for bulk visa application filings. These template files are notoriously rigid, and authoring them by hand against the agency's Excel macro requirements was previously a per-application bottleneck; the workflow now generates them programmatically through Claude-orchestrated MCP tools.

These are not aspirational use cases. They are what the team does daily.

### What stays outside the IDE

| Channel | Native UI usage | MCP usage |
|---|---|---|
| Slack | ~90% | ~10% (specific automated digest tools) |
| WhatsApp | ~100% | ~0% (planned MCP migration of `sugukuru-comms` not yet implemented) |
| Other SaaS (freee, GMO Bank, SmartHR remaining workflows, Google services) | ~30% | ~70% |

WhatsApp deserves a separate note: it is the primary channel for communication with foreign-language-native workers in remote agricultural locations. Wrapping it in MCP without losing the channel-native chat affordance is the focus of the planned `sugukuru-comms` migration. Until that migration ships, WhatsApp stays at 100% UI.

### Beyond MCP: direct Claude API usage from the integration hub

The MCP fleet is not the only path Claude takes into Sugukuru's stack. The integration hub (`sugukuru-hub`, the REST API service that wraps the MCP fleet's external SaaS integrations) also calls Claude API directly. Verified usage:

| Period | Sonnet 4.5 input tokens | Sonnet 4.5 output tokens | Spike notes |
|---|---|---|---|
| March 2026 | 224,548 | 54,737 | Sustained light usage |
| April 2026 (through 2026-04-15) | 1,358,725 | 650,279 | 5–6× month-over-month |

A single-day spike on 2026-04-04 — 1.24M input tokens, 584K output — was a month-end cycle running attendance computation, invoice generation, and Japan Immigration Services Agency bulk-application file authoring as a batched job. Month-end batches were the prior pre-MCP-era bottleneck and the first workload moved into the AI-augmented stack; the token volume reflects that.

The implication is not that direct API usage replaces MCP — it doesn't, the two coexist with different roles. MCP exposes structured tool surfaces for interactive workflows in Cursor/Antigravity; the direct API path handles batch operations that the integration hub orchestrates programmatically. The operator's stack uses both because the patterns serve different needs.

### What the GCP API surface tells us (30-day window)

The MCP fleet's GCP usage shows where computation actually lands. From the GCP project `sugukurucorpsite` (the deployment project hosting `sugukuru-core`, `sugukuru-finance`, `sugukuru-crm`):

| API | 30-day requests | Error rate | p50 latency | What it indicates |
|---|---|---|---|---|
| Google Drive | 29,099 | 0% | 235ms | Document workflows are Drive-mediated end-to-end |
| Cloud Build | 26,586 | 0% | 27ms | Continuous redeploy cadence reflects recursive bootstrapping |
| Secret Manager | 26,116 | 1% | 123ms | Credential operations are heavy in MCP auth flows |
| Cloud Run Admin | 16,829 | 0% | 57ms | Revision management is high-frequency |
| Cloud Logging | 11,000 | 0% | 96ms | Operational visibility is heavy |
| Cloud Document AI | 2,499 | **42%** | 2,196ms | Pattern 03 production usage with documented quality issues* |
| Gemini API | 2,452 | 11% | 3,435ms | Document AI fallback path |
| Container Analysis | 1,661 | 55% | 685ms | Vulnerability scanning, error pattern under investigation |

The Document AI error rate (42% over the 30-day window, p95 latency ~16 seconds) is a known operational reality not yet resolved. The operator reports that data-pipeline integration recently completed ("the data path is now in place"), and remediation is queued. This honest disclosure exists in this section because cookbook §3.1 requires that what is not yet solved be named alongside what is.

The Container Analysis error rate (55%) is similarly under investigation; cause unknown at the time of writing, and the failure mode does not currently block production operation but is on the team's queue.

### Tool growth trajectory (verified 2026-04-28)

The MCP tool surface has grown by approximately 20 distinct tool-additions over 90 days, distributed across 17 commits to the `aios` Python codebase (verified via `git log -G "@mcp.tool" -- "*.py" --since="90 days ago"`). The cadence:

- ~5–6 tool-related commits per month, sustained
- Multiple tool additions per commit are common: a single 2026-04 commit added five operations agents (dispatch document generation, financial analytics, legal ledger, petty cash, social insurance) in one merge

The pattern is what the cookbook tentatively names *operator-driven recursive bootstrapping*: a team member encounters a business need during ordinary work, asks Claude (via Cursor or Antigravity) to author the necessary MCP tool, deploys it to Cloud Run, and continues the workflow with the now-tooled operation available. There is no separate engineering sprint. There is no requirements document. The tool exists because someone needed it five minutes earlier.

This cadence is unusual relative to traditional internal-tooling cycles, where months pass between meaningful additions because each addition requires planning, scoping, building, and deploying as a discrete project. With Claude as authoring partner and MCP as the deployment substrate, the cycle compresses to hours.

### The receding subscription footprint

A second-order observation: as MCP coverage expanded, the team began retiring or downgrading third-party SaaS subscriptions that had previously been necessary for the workflows now covered by MCP tools.

- **SmartHR**: was used for social-insurance and unemployment-insurance form generation. As Claude (via MCP tools) became capable of generating these forms directly from the underlying data, the SmartHR subscription was downgraded — registered seats reduced from over 50 to under 50 (the contract's flat-rate threshold), with the contract running out the remaining annual commitment at the minimum tier and not renewing.
- **Adobe**: account count reduced as Claude-authored skills produced the documents Adobe products had previously been purchased for.

The economic implication is that "MCP coverage" and "SaaS subscription cost" are inversely correlated for workflows where MCP can plausibly replicate the SaaS's structured-data operations. This is not free — operating MCP servers has its own cost (~¥25,400/month Cloud Run plus ~$25/month Supabase) — but the trajectory is that infrastructure cost is replacing per-seat SaaS cost, and the math has so far favored the trade.

### How Sugukuru runs MCP without Smithery

Worth naming explicitly: the `sugukuru-core`, `sugukuru-finance`, and `sugukuru-crm` MCP servers are not published through Smithery or any other MCP registry. They are deployed as private Cloud Run services in the `sugukurucorpsite` GCP project, consumed by Cursor and Antigravity workspaces configured by the operator directly. Authentication is via API keys provisioned for the team's specific tools.

This is not an endorsement of any particular publication choice; some readers will find that publishing through a registry suits their access model better. It is recorded here because pre-publication drafts of the cookbook had assumed Smithery publication as the default, and the actual deployment runs without it. The operator's separate `suguvisa-mcp` project (out of scope for this case study; see project README) does use Smithery and is in MCP App registry review at the time of writing.

### What surprised us about IDE-as-UI

**The vocabulary of MCP-driven workflows enters the team's working language.** "Toh-goh" (突合 / reconciliation) is the canonical example. The verb describes the act of cross-checking invoice records against bank deposit records to find discrepancies — a tedious manual operation in the pre-MCP regime. Once Claude (driving MCP tools) began performing reconciliation as a routine step, the verb "toh-goh suru" entered the team's vocabulary not by management directive but by repetition. Team members watched Claude's reconciliation outputs flag discrepancies, learned to expect them, and adopted the verb. The operator now uses "toh-goh" in team meetings and Slack threads as if it had always been there. It hadn't; it had been a technical legal-accounting term that became operational vocabulary because MCP made the operation routine.

**MCP itself became a buzzword in the team's local context.** The operator reports that MCP is now widely discussed in their immediate professional network in Kagoshima, Japan — geographically and organizationally distant from the major AI-tooling discourse centers. This is anecdotal but worth recording: the patterns this cookbook documents are not running only in San Francisco or Tokyo.

**The "AI administrator" role replaces the "administrative staff" role.** Sugukuru's team uses the role term *AI 管理者* (AI administrator) in place of the conventional *事務員* (administrative staff) for the back-office function. The shift is not cosmetic. An administrative staff member's job is to execute structured tasks against admin dashboards. An AI administrator's job is to manage AI agents that execute those tasks, accepting or rejecting their outputs and authoring new tools when the agents lack capability. The two roles produce different outputs (the same workflows, but at different throughput per person) and require different skills (less SaaS-dashboard fluency, more IDE-and-prompt fluency). Whether this role redefinition generalizes outside Sugukuru's domain is an open question; the cookbook records that it has happened in one regulated-domain back-office.

**Non-engineers can become tool-authors with AI as authoring partner.** The 2nd-year team member's progression from non-engineer operations into a git-committing tool-author role is the cookbook's strongest piece of evidence that the IDE-as-UI pattern is not gated by prior engineering background. The required ingredients appear to be: an AI authoring partner (Claude in Cursor or Antigravity), sustained daily exposure, and access to a production fleet that absorbs tools as they are written. Whether this generalizes outside Sugukuru is unknown; that it has happened once is documented.

**SaaS replacement is not a deletion event.** Subscriptions retire gradually as MCP coverage reaches a usefulness threshold for each SaaS's workflows. The threshold varies by workflow. Some workflows reach it in days (form generation); others stay below it for months (anything channel-native, like Slack threads). The pattern is not "rip out all SaaS"; it is "MCP gradually absorbs the structured-data operations while channel-native UIs remain."

### Team trajectory (forward-looking note)

The four-person team described above is expanding: two engineers from Indonesia are scheduled to join in May 2026. The hiring pattern is itself worth recording — Sugukuru operates as a dispatcher of foreign workers under Japan's Specified Skilled Worker visa system, and it now hires foreign engineers to extend the MCP fleet that supports that business. The cookbook will revisit this case study after the new team members have been operating for a meaningful period (target: 3 months) to record what changes when the team grows from 4 to 6 — and from the current "two committers, two non-committers" mix to a different ratio.

This is recorded as a dated forward-looking note, not as a current operational fact. The cookbook does not claim a 6-person team today.

### What we have not solved

- **Tool-authoring quality assurance at the cadence of recursive bootstrapping.** Authoring an MCP tool during work is fast. Reviewing it for production-grade safety (correct annotations, idempotency, error handling) is not. The ratio of "tools authored quickly" to "tools reviewed thoroughly" is not currently measured. This is acknowledged technical debt.
- **Multi-team-member coordination on the IDE interface.** With four people now using the IDE interface in overlapping work sessions, lock-management at the database level becomes a non-trivial concern (Pattern 04 isolates by tenant, not by user-within-tenant). The deployment has not yet hit the constraint, but the team-size growth (toward 6 in May 2026) has put it on the radar.
- **Document AI quality at production scale.** The 42% Document AI error rate documented above is an honest operational gap. The operator has data-pipeline remediation queued, and a future iteration of this case study will report whether the queued fix lands.
- **OAuth-app composition not yet enumerated.** The 4× growth in OAuth-granted applications across the last six months (~38 → ~150) is corroborated by Google Workspace admin console data. The breakdown of those 150 applications (which are MCP-related, which are external SaaS integrations, which are individual Cloud Run service accounts, which are user-installed third-party tools) has not yet been catalogued. A future iteration will publish the breakdown.
- **Generalization to non-Japanese / non-regulated domains.** Sugukuru's specific stack (Japanese Specified Skilled Worker visa operations, Japanese banking integrations, Japanese-language regulatory templates) is heavily localized. Whether the IDE-as-UI pattern + AI-administrator role + recursive bootstrapping cadence generalizes to operators in other regulated domains in other languages is the obvious next experiment. This case study is one data point.

## Changelog

- **0.2.0** (2026-04-28): added Operator Experience section documenting four-person AI-administrator team, IDE-as-UI pattern with quantified Cursor analytics, GCP API surface metrics, OAuth-app long-term growth corroboration, and forward-looking team trajectory note. See [memo-errata §13](../../memo-errata.md#13) for the multi-hypothesis verification cycle that produced this section.
- **2026-04-28** — First published. Reconciled all factual claims against the `aios` codebase, GCP Console state, Supabase dashboard, and GCP Billing console before publication. Validates Patterns 01, 02, and 04. The pre-publication drafting included substantial corrections; see [`memo-errata.md`](../../memo-errata.md) for the record.
