---
title: "Memo Errata — Project Memos vs Verified Reality"
status: living
version: 0.5.0
last_reviewed: 2026-04-28
maintainer: "@sugukurukabe"
license: "Apache-2.0"
---

# Memo Errata

> **Purpose.** This file records claims that prior project memos, prior Claude session output, or human recollection asserted to be true, but which were later found to contradict higher-precedence evidence. It is a negative reference: a list of mistakes that the project has paid the cost of recovering from, kept on file so that the next session-Claude can avoid making them again.
>
> **How to read this.** Each entry has the same structure: the false claim, the verified truth, the source that established the truth, the chapters or files affected at the time of discovery, and a short note on how the false claim entered the project's knowledge. The `cookbook lessons` section at the bottom abstracts patterns across entries.
>
> **Per `OPERATIONS.md` C.3**, every discrepancy resolved during a Claude session MUST be recorded here. Adding to this file is a normal operational outcome, not a sign of failure.

---

## 1. The Memorystore Redis incident (2026-04-27)

### 1.1 The false claim

Prior project memos and Claude sessions stated:

> Sugukuru's MCP fleet uses Memorystore for Redis (Standard tier, single region) as an external session store. The fleet migrated from a "Path A" single-instance configuration to a "Path B" externalized session state implementation in late 2025, triggered when sustained concurrent sessions on `sugukuru-core` started crossing into the 10–15 range and `containerConcurrency: 80` began showing CPU saturation under tool-call bursts.

The claim was treated as deployment fact across at least three Claude sessions, propagated into draft Pattern 01 v0.1.0–v0.2.0, and into draft Case Study #01.

### 1.2 The verified truth

- **No Memorystore Redis instance exists in this GCP project.** The `redis.googleapis.com` API is in the unenabled state (the Console displays an "Enable" button), as is `memorystore.googleapis.com` (Valkey).
- **No `REDIS_*` environment variables exist on any of the four MCP services or `sugukuru-hub`.**
- **GCP Billing through 2026-04-26 contains no Memorystore line item.**
- **No Path A → Path B migration occurred.** Initial revisions of `sugukuru-core`, `sugukuru-finance`, and `sugukuru-crm` were created on 2026-03-22 with `containerConcurrency: 80` already set; that value has not been changed across revisions. The "12 sustained sessions" threshold was not measured. It was a phrase generated during a writing pass and treated as fact in subsequent passes.
- **The actual session continuity mechanism** is `run.googleapis.com/sessionAffinity: "true"` plus `min-instances: 1` on `sugukuru-core` (per the Cloud Run YAML, line 42). This produces the same result the false claim attributed to Redis: a session is pinned to a warm instance that holds in-memory session state, with the 300-second GET reconnect cycle re-pinning to the same instance via cookie.

### 1.3 Source establishing the truth

- GCP Console snapshot, 2026-04-27, showing Redis and Memorystore APIs unenabled.
- `gcloud run services describe` output for `sugukuru-core` showing `sessionAffinity: "true"` annotation.
- Cloud Run revision history showing initial-revision concurrency at 80.
- GCP Billing console MTD view as of 2026-04-26.
- `deploy-mcp-split.sh` lines 78–92 establishing initial deployment configuration.

### 1.4 How the false claim entered

A prior session Claude wrote a Pattern 01 draft that explicitly recommended Path B (externalized session state via Redis) as the mature configuration. In a separate writing pass, claims about Sugukuru "using" Path B were inserted as supporting evidence to make the recommendation feel grounded. No verification step was performed against GCP state. Subsequent sessions imported these claims as established facts via the handoff memo, deepening the error.

### 1.5 Cost of recovery

- Drafting and discarding two pattern revisions (v0.1.0 and v0.2.0 of Pattern 01).
- Multiple Claude sessions of correction work.
- Establishment of the OPERATIONS.md → gcp-verified-facts.md → memo-errata.md three-file regime to prevent recurrence.

### 1.6 Lasting correction

Pattern 01 v0.3.x reframes the three paths as concurrent role-based options (warm baseline for critical services, scale-to-zero for secondary, externalized state for overflow), with Sugukuru documented as a Path A + Path B deployment. The corrected chapter is stronger than the chapter the false claim was supporting; the actual mechanism is more interesting than the fabricated one.

---

## 2. The "October 2025 first live traffic" claim (2026-04-27)

### 2.1 The false claim

> First live traffic: October 2025.

### 2.2 The verified truth

- `sugukuru-core` initial revision `00001-kss` created `2026-03-22T05:56:44.075064Z`.
- `sugukuru-finance`, `sugukuru-crm` initial revisions created on the same date.
- GCP Billing graphs show cost rising from approximately `2026-03-22` onward.

The fleet has been in live operation for approximately **5 weeks** as of 2026-04-28, not 6 months.

### 2.3 Source

Cloud Run revision history, GCP Billing graphs.

### 2.4 How the false claim entered

A prior session Claude conflated "the project was conceived" with "the fleet entered live operation." The two events were several months apart.

---

## 3. The tool-count claim (2026-04-27 / 2026-04-28)

### 3.1 The false claim, version 1

Early Pattern 02 drafts stated: "approximately 30 tools at Sugukuru Inc." Separately, narrative claimed "core ~30 + finance ~12 + crm ~15." The two figures are not arithmetically reconcilable.

### 3.2 The false claim, version 2

A subsequent reconciliation pass stated **117 tools across the fleet**. This number was used in early Antigravity drafts of Pattern 04.

### 3.3 The verified truth

**115 unique MCP tool definitions** registered across `sugukuru-core`, `sugukuru-finance`, and `sugukuru-crm`, confirmed by direct codebase inspection on 2026-04-28 (commit `a0ab310`).

### 3.4 How the false claims entered

Version 1: round-number heuristic in early drafting, propagated as fact.

Version 2: code inspection that double-counted two tools registered under aliases. Caught and corrected in commit `a0ab310: fix: correct tool count 117→115, full re-verification against codebase`.

### 3.5 Lasting correction

`gcp-verified-facts.md` §3.2 records 115 as the verified count. Cookbook chapters cite 115 with the source.

---

## 4. The "Q1 2026 annotation review" claim (2026-04-27)

### 4.1 The false claim

> The annotation set was reviewed against the Japanese Immigration Control Act and Worker Dispatch Law in Q1 2026, with updates committed under tool-versioning rules.

### 4.2 The verified truth

A formal, documented annotation review against specific statutory provisions has not been published. Tool annotations were assigned with awareness of the relevant laws from project inception, but no review document exists.

### 4.3 How the false claim entered

A prior session Claude inferred from context that such a review must have happened, and committed the inference to text without flagging it as inference.

### 4.4 Lasting correction

Pattern 02 and Case Study #01 now state that annotations "have been assigned with awareness of" the laws "from project inception" and that "Pattern 02 itself represents the framework that future review will follow."

---

## 5. The fabricated upstream incidents (2026-04-27)

### 5.1 The false claim

> Outages we have had were upstream API issues (one freee API incident; one transient Vertex AI Search timeout cluster).

### 5.2 The verified truth

Both incidents were fabricated by a prior session Claude. Neither occurred.

### 5.3 How the false claim entered

The chapter section was prompting for examples of upstream issues. The Claude generated plausible-sounding ones to fill the section rather than reporting absence.

### 5.4 Lasting correction

The current Case Study text states only what is verified: that there are no MCP-layer outages in operational records to date.

---

## 6. The "sugukuru-gateway" naming claim (2026-04-27)

### 6.1 The false claim

Early drafts of Pattern 01 named the four MCP servers as `sugukuru-core`, `sugukuru-finance`, `sugukuru-crm`, and **`sugukuru-gateway`**.

### 6.2 The verified truth

There is no service named `sugukuru-gateway` in the GCP project. The fourth name, originally listed in memos, is `sugukuru-comms` — and even that turned out not to be an MCP server (see §8 below).

### 6.3 Lasting correction

No occurrence of `sugukuru-gateway` remains in any current draft.

---

## 7. The runtime claim — TypeScript on Bun vs Python on FastMCP (2026-04-28, RESOLVED)

### 7.1 The false claim

Earlier project memos and `antigravity-handoff-bundle.md` v1 stated the runtime was **TypeScript on Bun**. This claim propagated through multiple Claude sessions.

### 7.2 The verified truth

The MCP fleet runs on **Python 3.12 + FastMCP** for `sugukuru-core`, `sugukuru-finance`, and `sugukuru-crm`. `sugukuru-comms` runs on Node.js (but is a webhook, not an MCP server — see §8).

The verification source is direct inspection of the `aios` Python codebase (the monorepo containing `sugukuru-core`, `sugukuru-finance`, `sugukuru-crm`, and `sugukuru-hub` source).

### 7.3 How the false claim entered

The "TypeScript on Bun" stack is correct for **`suguvisa-mcp`**, a separate TypeScript MCP project at https://github.com/sugukurukabe/suguvisa-mcp, in a separate GCP project, anticipated to be split into a separate company in mid-2026. An earlier Claude session conflated the two projects: `suguvisa-mcp` (TS/Bun) was misidentified as the runtime stack of the `sugukuru` MCP fleet (Python/FastMCP).

This is a useful instance of the lesson "memos lie": the human-recorded memo described a real codebase (TS on Bun) but attached the description to the wrong project.

### 7.4 Lasting correction

`gcp-verified-facts.md` §1.1 records Python 3.12 + FastMCP as the runtime for the three live MCP servers. The cookbook does not currently document `suguvisa-mcp`; it will become Case Study #02 after the planned mid-2026 corporate split.

---

## 8. The `sugukuru-comms` MCP server claim (2026-04-28, RESOLVED)

### 8.1 The false claim

Earlier drafts of Pattern 02, Case Study #01, and `gcp-verified-facts.md` v0.1–v0.2 described `sugukuru-comms` as a fourth MCP server with the following properties:
- WhatsApp Business API integration with an AI-orchestrated multi-agent layer
- Six specialist agents (workplace coordination, safety/labor-standards, daily-life, learning, health, emergency escalation)
- All tools annotated `openWorldHint: true`
- Message-send tool annotated `destructiveHint: true`
- Cited as the canonical example for Pattern 02's `openWorldHint` boundary discussion

### 8.2 The verified truth

`sugukuru-comms` is currently a **vanilla Node.js Express application acting as a WhatsApp Business API webhook receiver**. It contains **no MCP tools, no MCP transport, no `Mcp-Session-Id` handling**. It strictly routes inbound WhatsApp messages.

The multi-agent orchestration described above is the **planned future state** when `sugukuru-comms` is migrated to MCP. The migration is anticipated but not scheduled.

### 8.3 Source

Codebase inspection of the `sugukuru-comms` repository, 2026-04-28.

### 8.4 How the false claim entered

The operator's strategic vision for `comms` (as articulated in conversation: "AI orchestration that routes worker inquiries to specialist agents and emits multilingual responses") was treated by an earlier Claude session as a description of the current implementation. The future-tense aspiration was rendered in present tense, then treated as deployment fact in subsequent passes.

### 8.5 Lasting correction

- `gcp-verified-facts.md` §1.2 lists `sugukuru-comms` under "Confirmed non-MCP supporting services" with its current role (webhook receiver) and its planned future role (MCP migration) clearly distinguished.
- Pattern 02 no longer cites `sugukuru-comms` as the `openWorldHint` example. The principle of trust-boundary isolation by server is preserved as a general design recommendation; the specific Sugukuru example is reserved until the migration occurs.
- Case Study #01 describes `sugukuru-comms` as "currently a webhook, future MCP migration planned" without further claims about its tool inventory or annotation surface.

---

## 9. The accidentally-published Japanese files (2026-04-28)

### 9.1 The false claim (by omission)

The cookbook's `cookbook-strategy-principles.md` §4.1 declares English-only publication as a MUST. Despite this, the initial repository state on 2026-04-28 included six Japanese-language files: `README.ja.md`, four `*.ja.md` patterns, and one `*.ja.md` case study. These were published to the public repository before the strategy file's English-only rule was committed.

### 9.2 The verified truth

The strategy is English-only. The Japanese files were a violation of that strategy and were authored by an Antigravity Claude session that did not have access to `cookbook-strategy-principles.md` (which had not yet been committed to the repository at that point).

### 9.3 Source

Direct inspection of the `mcp-regulated-cookbook` repository at HEAD commit `a0ab310`. The Japanese files were present in the working tree.

### 9.4 How the false claim entered

A coordination gap: the strategy file (English-only MUST) was authored in a different Claude session than the chapter-authoring Antigravity session. The Antigravity session had no access to the strategy file at the time it ran; with no English-only rule visible to it, it produced bilingual chapters as a reasonable default for a Japanese-operator project.

### 9.5 Lasting correction

- The Japanese files were removed from the repository on 2026-04-28 before any external readers could mistake them for sanctioned bilingual coverage.
- `cookbook-strategy-principles.md` was committed to the repository at the same time, making the English-only rule visible to all subsequent sessions.
- `OPERATIONS.md` Section A.1 added the requirement that all sessions consult the strategy file before chapter-authoring.
- This errata entry exists so future sessions understand why English-only is enforced and what happens when the rule is invisible.

---

## 10. The active-worker count (2026-04-28)

### 10.1 The competing claims

| Source | Claim |
|---|---|
| Operator self-report | "150+ steady-state active workers" |
| Antigravity codebase inspection | "400+ workers (Supabase staff table)" |

### 10.2 The verified truth

Both are correct, but they describe different populations:

- **150+** is the active steady-state worker count under MCP-driven case management — workers whose visa cases, dispatch contracts, and payroll are currently being processed.
- **400+** is the all-time record count in the Supabase `staff` table — including historical, retired, transferred, and otherwise-inactive workers retained for compliance/audit purposes.

### 10.3 Cookbook usage

Per `gcp-verified-facts.md` §9: cookbook chapters use **150+** when describing the operational scale of MCP-driven processing. The 400+ figure may appear when explicitly framed as the table record count, not as the active worker base.

### 10.4 How the discrepancy arose

The operator's strategic communications use 150+ (the meaningful business metric). Codebase inspection naturally returns 400+ (the actual database row count). A previous Claude pass (Antigravity) used the 400+ figure as the cookbook headline number, which would have over-stated the active operational scale by ~2.6x.

---

## 11. The "production" terminology ambiguity (2026-04-28, RESOLVED before initial publication)

### 11.1 The ambiguous term

Pre-publication drafts of multiple cookbook chapters used `production` to describe Sugukuru's MCP fleet. The deploying organization is a small operator running its own internal business operations — not selling the MCP fleet as an external product. The English word `production` does not distinguish between "running real business operations on real data" and "sold as a product to external customers"; both readings are colloquially valid.

### 11.2 Why this matters for the cookbook

The cookbook's audience includes prospective partners and investors who would interpret `production` differently than the case study author intended. A reader assuming the "external product" reading would over-estimate the deploying organization's commercial maturity.

### 11.3 The verified intent

Sugukuru runs the MCP fleet for its own real business operations, not as an external product. Active operational load (150+ workers under live case management, 74,789 7-day request volume on Supabase, real freee + GMO Bank integrations executing real money movements) qualifies as live deployment in every meaningful technical sense. The deployment does not, however, qualify as an "external product" because Sugukuru does not offer the MCP fleet for purchase.

### 11.4 Lasting correction

- Cookbook prose now uses `live operation` / `live deployment` throughout when describing the deployment's status.
- `production` is retained only when it refers to a cloud-platform environment tier (e.g., "Cloud Run production traffic"), where it is a technical adjective and the ambiguity does not arise.
- `cookbook-strategy-principles.md` §2.4 codifies the distinction as a [MUST] rule.
- `README.md` "What this is" section explicitly notes the cookbook's "live" usage.
- Case Study #01's lead clarifies that the deployment is internal-only.

### 11.5 How the ambiguity entered

A pre-publication Claude session adopted `production` as the default term, following industry convention without distinguishing between the "external product" usage and the "internal live operations" usage. The operator caught the ambiguity during pre-publication review of bundle text. The correction was applied before initial publication; readers of the cookbook never saw the ambiguous version.

---

## 12. The pre-publication scout component (2026-04-28, RESOLVED before initial publication)

### 12.1 The premature inclusion

Pre-publication drafts included `tools/cookbook-scout/`, `docs/scout/SPEC.md`, `docs/scout/INTEGRATION.md`, and `scripts/cookbook-candidate-detector.sh` as cookbook contents, with corresponding references in `README.md`, `cookbook-strategy-principles.md` §9, `docs/patterns/INDEX.md`, and `OPERATIONS.md`.

The `mcp-cookbook-scout` MCP server existed only as a design specification — no implementation, no deployment, no live traffic, no recorded usage. The bash hook (`cookbook-candidate-detector.sh`) had been authored but had never been installed in any repository or scored any commit.

### 12.2 The principle violated

`cookbook-strategy-principles.md` §2.1 requires that cookbook contents be grounded in at least one live deployment. The scout substrate violated this directly. While §2.1's letter applies to patterns and case studies, the cookbook's broader honesty principle (§3.1) extends to all advertised contents — a `## Tools` section in `README.md` advertising vaporware would have given readers a false impression of the cookbook's substance.

This is also a direct application of Lesson 6 from this errata file: "Cookbook honesty produces stronger chapters than fabricated cleanliness." Removing the unimplemented scout is the honesty-over-polish move.

### 12.3 What was removed

- `tools/cookbook-scout/` directory (placeholder README only, never had source code)
- `docs/scout/SPEC.md` (548-line design specification)
- `docs/scout/INTEGRATION.md` (276-line integration plan)
- `scripts/cookbook-candidate-detector.sh` (244-line bash hook implementation, never installed)
- "Tools" section in `README.md`
- §9 in `cookbook-strategy-principles.md` (later sections renumbered to §9, §10, §11)
- "Cookbook Self-Observation" entry in `docs/patterns/INDEX.md` proposed-patterns list

### 12.4 Future reintroduction

The scout concept is sound and the design specification has value. Both will return to the cookbook in a future version (v0.2.x or later) under the following conditions:

- The scout MCP server has been implemented (V0 deploy meeting the design specification's tool surface).
- The scout has been deployed in at least one operator's environment.
- The scout has run long enough to have actually surfaced cookbook-contribution candidates from real development activity.
- The deployment qualifies as a "live deployment" per `cookbook-strategy-principles.md` §2.4 and merits a case study.

When these conditions are met, the scout will reenter the cookbook with its own case study, real live-deployment metrics, and accurate description of what it is rather than what it is intended to be.

### 12.5 How the premature inclusion happened

The pre-publication Claude session that drafted the cookbook's initial structure recognized scout as a strategically valuable differentiator (a self-observation MCP server is rare among cookbooks) and prioritized including it in the v0.1.0 launch. The session weighed strategic positioning against the live-deployment-grounding rule and resolved the trade-off by including the design without flagging that "design only" should not appear in a published cookbook claiming to document what operators run.

The operator caught this in pre-publication review, asking "but we haven't built or run this — what is it?" The strategic answer (it would be valuable for differentiation) did not survive contact with the cookbook's own honesty rules.

This is the cookbook's own §3.1 (honesty over polish) and §2.1 (live-deployment grounding) being applied to itself, in front of any external reader. The cookbook benefits from this incident as direct evidence that it follows its own rules.

---

## 13. Pre-publication hypothesis verification — IDE-as-UI, Recursive Bootstrapping, Two-stage Operations, and Single-Operator Framing (2026-04-28, RESOLVED before initial Operator Experience publication)

This entry records a multi-hypothesis verification cycle conducted before publishing the Operator Experience section in Case Study #01. Four hypotheses about Sugukuru's deployment were examined in pre-research drafting; codebase inspection, operator interview, and direct usage instrumentation refined two, rejected one at the layer where it was claimed to operate, and overturned a fourth entirely. Recording all four together here because the cycle illustrates how the cookbook applies its own §2.1 (live-deployment grounding) and §3.1 (honesty over polish) rules to its own draft contents.

### 13.1 The "No-UI Architecture" hypothesis (refined, not rejected)

**The original hypothesis.** A pre-research draft characterized Sugukuru as running its back-office "without traditional admin UI", driving 100% of operations through Cursor and Antigravity. This was rhetorically attractive — "the IDE is the office" — and would have been a strong cookbook differentiator if true.

**The verified truth.** A `sugukuru-os-v4` Next.js application exists in the repository with 24 pages and 85 API routes, currently in test deployment for specific human-in-the-loop approval flows. SaaS native UIs (Slack at ~90% native, WhatsApp at 100% native, miscellaneous SaaS at ~30% native) remain in active use. The Supabase Dashboard is used for ad-hoc DB operations.

The honest version of the hypothesis: the IDE pair (Cursor + Antigravity) is the **primary** interface for over 50% of administrative work, but it is not the **sole** interface. The architecture is dual: IDE for structured-data operations, native SaaS UIs for channel-native operations, `sugukuru-os-v4` for approval flows.

**How the false claim entered.** A pre-research drafting pass adopted "No-UI" as shorthand for "IDE-primary." The shorthand survived into the draft. It was caught when Antigravity's codebase investigation found `sugukuru-os-v4` and asked whether the claim was accurate — the operator's answer ("test deployment, used for specific approval flows") refined the claim into the dual-interface description that ships in the published Operator Experience section.

**Lasting correction.** The Operator Experience section now opens with the explicit dual-interface reality, naming all four interface types and their respective scope. The cookbook gains specificity from refusing to overstate.

### 13.2 The "Recursive Bootstrapping" hypothesis (initially under-counted, then verified)

**The original hypothesis.** Sugukuru's operational pattern is one of "recursive bootstrapping" — the operator encounters a tedious task, asks Claude (via Cursor/Antigravity) to author an MCP tool for it, deploys, and continues with the new tool available.

**The first investigation.** An Antigravity research session inspected git log for the past 30 days and concluded that the hypothesis was "not supported by evidence" because tool-addition commits were not visible at the cadence the hypothesis implied.

**The corrected investigation.** A direct git log query expanding the window to 90 days, with the search anchored on `@mcp.tool` decorator additions, revealed approximately 20 distinct tool-additions across 17 commits — averaging 5–6 tool-related commits per month, with multiple tool additions common per commit. Independent verification via the GitHub compare view of the 30-day window showed 93 commits touching 1,293 files from 2 contributors, supporting the same conclusion at higher resolution.

The first investigation had likely under-counted because:
- 30 days is too short a window for the per-tool cadence (many tools are added per commit, not every commit adds a tool)
- Tool additions were grouped into batched commits with non-tool commit messages, making naive grep miss them
- The pattern operates at the level of `@mcp.tool` decorator additions inside files, not at the level of new files appearing

**The verified truth.** Recursive bootstrapping is real and at a sustained cadence unusual for traditional internal-tooling cycles. The published Operator Experience section names this pattern and cites the verification commands.

**How the under-count happened.** Investigation methodology bias: the researcher applied a 30-day window because the hypothesis felt "should be visible at high cadence" and the evidence not appearing in that window read as falsification. The honest move was to extend the window and try different search anchors, which is what produced the verified count.

### 13.3 The "Two-stage Destructive Operations" hypothesis (rejected at MCP layer; found at frontend layer)

**The original hypothesis.** High-risk operations (bank transfers, regulatory filings) are implemented as paired tools — `prepare_X` (non-destructive) and `commit_X` (destructive) — with human approval between the prepare and commit calls. Tool annotations carry `destructiveHint: true` on the commit-stage tool.

**The verified truth.** Codebase inspection found:
- No tool definitions matching the prepare/commit naming pair pattern
- No use of `destructiveHint` annotations in the `aios` codebase

Human-in-the-loop approval IS implemented in the deployment, but at a different layer: `sugukuru-os-v4` contains an `execution-modal.tsx` component for approval-gated execution flows, and the actual two-stage pattern lives in the frontend Next.js application, not in the MCP server tool definitions.

**Why this matters for the cookbook.** The hypothesis was correct in spirit (high-risk operations are gated by human approval) but wrong about the layer (it is a UI-layer pattern in the frontend, not a tool-layer pattern in the MCP server). The cookbook does not currently document the frontend-layer pattern because the frontend is not yet in the cookbook's scope. The Operator Experience section notes that approval flows exist for specific operations and points readers to the dual-interface reality without overclaiming where the gating lives.

If a future case study or pattern documents the frontend-layer pattern explicitly, it would extend the cookbook into territory currently out of scope — a separate decision.

**Lasting correction.** The Operator Experience section does not claim Sugukuru implements two-stage MCP tool patterns. The proposed Pattern 02 example for prepare/commit tool pairing now references this errata entry to make explicit that the example is illustrative of the recommended approach, not a description of Sugukuru's current implementation.

### 13.4 The "Single Operator" framing (overturned by usage instrumentation)

**The original hypothesis.** Pre-research drafts assumed Sugukuru's MCP fleet is driven by a single operator (the CEO/CTO), with the IDE-as-UI pattern dependent on that operator's individual technical capacity.

**The verified truth.** Cursor team analytics over the 30-day window 2026-03-30 to 2026-04-28 show **daily active users ranging from 1 to 4, averaging 2.1, with active usage on 29 of 30 days**. All four members of Sugukuru's back-office team use Cursor and Antigravity daily. Independent verification via GitHub compare for the same window shows **2 git contributors** (the CEO/CTO and one 2nd-year team member who has progressed from a non-engineering operations background into a tool-authoring role). The remaining two team members drive Cursor sessions for back-office work without committing code directly. The team has explicitly retired the role term "administrative staff" (事務員) and replaced it with "AI administrator" (AI 管理者).

**How the original framing entered.** The pre-research draft assumed that "IDE-as-UI" implied single-user operation because the IDE is a developer tool and developers conventionally work individually. The assumption was inherited rather than verified. It was caught when the operator supplied direct Cursor analytics CSV exports showing multi-user activity, supplemented by the GitHub compare view confirming two distinct git committers.

**Why this matters for the cookbook's substantive claim.** The single-operator framing, if it had been published, would have undersold the pattern's significance. "One technical operator can drive 116 MCP tools through an IDE" is a moderately interesting observation. "A four-person team consisting of one CEO/CTO, one non-engineer-graduated tool-author, and two non-committing IDE users can drive 116 MCP tools through an IDE, replacing administrative-staff seats with AI-administrator roles" is a substantively different and more consequential claim. The corrected version is what ships, and it is also the cookbook's first concrete data point that the IDE-as-UI pattern admits non-engineer team members into tool-authoring roles given enough time and AI-pair-authoring scaffolding.

**Lasting correction.** The Operator Experience section opens with the team composition explicitly. The "AI administrator" role term is named and defined. The DAU range, AI-authored line ratio (~81%), 30-day agent request count (2,685), and 30-day commit cadence (93 commits / 1,293 files / 2 contributors) are published as direct usage evidence rather than as the operator's recollection.

### 13.5 Cross-entry observations

These four hypothesis verifications, taken together, are the cookbook's clearest demonstration so far of Lesson 7 (the cookbook applies its own rules to itself) operating in practice.

The pre-research drafts, if published, would have contained:
- An overstated "No-UI" architecture claim (§13.1)
- An under-counted recursive-bootstrapping pattern, initially erased then incorrectly framed (§13.2)
- A misattributed two-stage operations pattern, claimed in MCP layer but actually in UI layer (§13.3)
- A single-operator framing that would have understated the pattern's significance by a factor of four (§13.4)

All four were caught before initial publication of the Operator Experience section because the cookbook applied §2.1 (live-deployment grounding) and §3.1 (honesty over polish) to its own draft. None of these would have been caught by the cookbook's editorial principles if the principles had been treated as suggestions rather than rules.

**A pattern within the pattern.** §13.2 (under-counted then corrected) and §13.4 (under-claimed then expanded) share a structure: the pre-research framing was a *narrower* version of the truth than the data supports. This is the inverse of the more common failure mode (overstating). The cookbook's standard for these cases is the same as for overstating: re-frame to fit the evidence, in either direction.

The cookbook's value to readers depends on the principles being load-bearing. Recording this cycle in the errata file is part of the load.

---

## Cookbook lessons across entries

The thirteen entries above share recurring failure modes. Recording them here for the project's benefit.

### Lesson 1: Plausible-sounding numbers are the most dangerous claims

Entries §1 (Memorystore + 12 sessions threshold), §3 (~30 tools, then 117), §5 (one freee incident, one Vertex cluster) all involve specific, round, plausible numbers that no one had actually measured. The plausibility is the trap; a wildly wrong number gets challenged, a "looks about right" number does not.

OPERATIONS.md B.3 ("any sentence containing a number is traceable to gcp-verified-facts.md") is the procedural counter-measure.

### Lesson 2: Inference-as-fact is the dominant entry pathway

Entries §1, §4, §5, §6, §8 each entered the project's knowledge as a Claude inference that was treated as fact in subsequent sessions because the inference markers had been smoothed away during writing.

OPERATIONS.md A.1 (consult `gcp-verified-facts.md` at session start) and C.4 (uncertainty disclosure) are the procedural counter-measures.

### Lesson 3: Cross-project conflation is silent

Entry §7 (TS on Bun vs Python on FastMCP) and entry §8 (`sugukuru-comms` as MCP) both arose from conflating descriptions of the wrong project with the project at hand. The error is silent because the descriptions are internally coherent — they just describe a different system.

The procedural counter-measure: when adopting any factual claim from a memo, verify the **subject** of the claim, not just the **content**. "Which codebase does this paragraph describe?" is the question that catches §7 before it becomes Pattern 01's runtime claim.

### Lesson 4: Future tense becomes present tense

Entry §8 (`sugukuru-comms`) is the canonical example. The operator's vision for what `comms` will become was, in a writing pass, rendered as a description of what `comms` is. This is a writing failure (verb tense) but it propagates as a verification failure (the next session reads "is" and treats the claim as current).

OPERATIONS.md B.2's prohibition on inventing claims to make a paragraph feel concrete is the counter-measure, but vigilance against verb-tense drift is its own discipline.

### Lesson 5: Coordination gaps create rule violations

Entry §9 (Japanese files) is the only entry that originated from coordination failure rather than memo or session error. The Antigravity session that produced the violation had no access to the strategy file forbidding it. Once the strategy file became visible, the violation was immediately recognized and removed.

OPERATIONS.md E.1 (handoff in: include `OPERATIONS.md` in the handoff) is the counter-measure. Distinct from inference-as-fact, this is rule-not-yet-published-fact.

### Lesson 6: Cookbook honesty produces stronger chapters than fabricated cleanliness

In every entry where the false claim was replaced with the verified truth, the resulting chapter was *stronger*. Sugukuru's actual session-continuity mechanism (sticky cookie + warm baseline, no Redis) is more interesting than the false Memorystore claim. The actual 5-week operational duration is more salient than the fabricated 6-month one. The actual annotation framework being the cookbook itself is a more honest alignment than a fictional review. The actual codebase (Python/FastMCP, 115 tools, Supabase Micro at $25/mo) is a more compelling case study than the imagined version.

This is a useful prior for future drafting: when in doubt about whether to fabricate a confident claim or admit absence, admit. The corrected chapter tends to be better.

### Lesson 7: The cookbook applies its own rules to itself

Entries §11 (production terminology) and §12 (scout removal) are different from §1–§10 in one important way: they were caught and resolved **before** initial publication, by the operator applying the cookbook's own published rules to the cookbook's own draft contents. §11 enforced `cookbook-strategy-principles.md` §3.2 (specificity over generality) against ambiguous terminology. §12 enforced §2.1 (live-deployment grounding) against vaporware components.

The procedural counter-measure for both was the same: the operator read what the cookbook claimed to be, compared it to what was being shipped, and refused to ship the gap. The cookbook's standards work as standards only when someone actually applies them, including against material the cookbook is itself producing.

Future Claude sessions, future contributors, and future maintainers SHOULD apply the same scrutiny to cookbook drafts as they would to any third-party submission. The cookbook's editorial principles do not exempt their authors.

---

## Changelog

- **0.5.0** (2026-04-28): added §13 (pre-publication hypothesis verification cycle for IDE-as-UI / Recursive Bootstrapping / Two-stage Operations / Single-Operator framing); thirteen entries total
- **0.4.0** (2026-04-28) — Added §11 (production terminology ambiguity) and §12 (pre-publication scout component) to record corrections that were applied to the v0.1.0 integration commit but had not been documented in this errata file at that time. Added Lesson 7 (the cookbook applies its own rules to itself). Skipped 0.3.0 to mark this as a meaningful catch-up; the entries were always supposed to be there.
- **0.2.0** (2026-04-28) — Added §7 (runtime resolution: Python/FastMCP), §8 (`sugukuru-comms` is webhook, not MCP), §9 (Japanese files removal), §10 (active-worker count reconciliation). Cross-entry lessons updated: added Lesson 3 (cross-project conflation), Lesson 4 (future→present tense drift), Lesson 5 (coordination gaps).
- **0.1.0** (2026-04-28) — Initial publication. Records six errata entries spanning the 2026-04-27/28 window of cookbook drafting and reconciliation.
