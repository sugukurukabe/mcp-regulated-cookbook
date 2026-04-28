---
title: "Operations Manual for the mcp-regulated-cookbook Project"
status: living
version: 0.1.0
last_reviewed: 2026-04-28
audience:
  - "Claude (in Claude Projects, Antigravity, Cursor, or Claude Code)"
  - "Sugukuru Inc. team members working on the cookbook"
license: "Apache-2.0"
---

# Operations Manual

> **Purpose.** This file defines how the `mcp-regulated-cookbook` project is operated. It applies to every Claude session in the project, every Antigravity session referencing the project, and every human contributor (currently one — but written so additional contributors can onboard from this file alone).
>
> **Conformance language.** This document uses MUST / SHOULD / MAY in the sense of [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). MUST is non-negotiable; violating it is a project-defect. SHOULD is the strong default; deviation requires a documented reason. MAY is permissive.
>
> **How to read this.** Part I (Sections A–E) is normative procedure. Part II is reference material — the `why` behind Part I. Claude sessions MUST read Part I at session start; Part II is consulted on demand.

---

# Part I — Procedures

## A. Session-start procedure

**Audience: Claude in any tool (Claude Projects, Antigravity, Cursor, Claude Code).**

When a new session opens against this project, Claude MUST perform the following before producing any cookbook-affecting output.

### A.1 Knowledge orientation [MUST]

Claude MUST locate and consult the following project-knowledge files (or their equivalents in the current tool's knowledge base) before answering any cookbook-substantive question:

1. This file (`OPERATIONS.md`)
2. `cookbook-strategy-principles.md` (immutable strategic rules)
3. `gcp-verified-facts.md` (the truth ledger — overrides any other source on factual claims)
4. `memo-errata.md` (errors made in prior sessions; negative reference)

If the active tool does not expose project-knowledge search (e.g., a fresh Cursor workspace without configuration), Claude MUST request the user load these files, or refuse to make factual claims about Sugukuru's deployment until they are loaded.

### A.2 Spec orientation [SHOULD]

For any cookbook task that touches MCP protocol behavior, Claude SHOULD also consult:

- `mcp-spec-2025-11-25-transports.md`
- `mcp-spec-2025-11-25-authorization.md`
- `mcp-spec-2025-11-25-tools.md`
- `mcp-spec-2025-11-25-changelog.md`

If these are absent from project knowledge, Claude SHOULD note the absence in its response and either fall back to its training-time knowledge with a confidence caveat, or request the files be loaded.

### A.3 Mode declaration [SHOULD]

At the start of any non-trivial cookbook task, Claude SHOULD state in 1–2 sentences which procedural mode the upcoming work falls under:

- `chapter-authoring` — writing or revising a Pattern or Case Study
- `fact-verification` — confirming a deployment-specific claim
- `strategic-discussion` — non-cookbook strategy aligned with v3 strategy book
- `operational-housekeeping` — updating OPERATIONS.md, errata, status
- `tool-implementation` — writing code for cookbook tooling

Mode declaration is for the human's benefit. It signals which checklist (Section B, C, D, etc.) governs the task.

### A.4 Tool discovery [MAY]

Claude MAY, at session start, run `tool_search` to discover deferred tools relevant to the task. This is encouraged for `fact-verification` mode (where GCP, Slack, or git tools are commonly needed).

---

## B. Chapter-authoring procedure

**Audience: Claude in `chapter-authoring` mode.**

This procedure applies to writing or revising any file under `docs/patterns/` or `docs/case-studies/`.

### B.1 Pre-writing checks [MUST]

Before writing or modifying a chapter, Claude MUST:

1. Verify that the claim domain (e.g., "session continuity," "tool annotations") does not duplicate an existing chapter's scope. Read `docs/patterns/INDEX.md` and `docs/case-studies/INDEX.md` first.
2. Read the relevant entries in `gcp-verified-facts.md` for any deployment-specific claims to be made.
3. Identify which sections of MCP spec 2025-11-25 will be cited; verify the citations against the spec files in project knowledge.


### B.2 Authoring constraints [MUST / SHOULD]

While writing, Claude MUST:

- Write in English. Japanese drafts are permitted in scratch files outside `docs/` but MUST NOT be merged into the cookbook.
- Stay under 3,000 words per pattern. Case studies SHOULD be under 2,500 words; longer is acceptable when the case includes substantial numerical evidence.
- Include all mandatory sections per `docs/patterns/_TEMPLATE.md` (for patterns) or the case-study skeleton (for case studies).
- Cite specific spec sections, SDK versions, and platform features by name. "A serverless platform" is NOT acceptable; "Google Cloud Run with `min-instances: 0`" is.
- Ground every deployment claim in `gcp-verified-facts.md` or a specific named source (Cloud Run YAML line number, Cloud Logging timestamp, GCP Billing date). Claude MUST NOT invent quantitative claims to make a paragraph feel concrete.
- Use the Cookbook tone: "warning a colleague about a real failure." Marketing voice ("seamlessly integrate," "best-in-class") is forbidden.

While writing, Claude SHOULD:

- Open with a one-sentence summary in italic blockquote at the top of the chapter.
- Include a "When this pattern fails" section (falsifiability). A chapter without this is a drafting defect.
- Number `version: x.y.z` per semver: x = breaking restructure, y = added section or path, z = wording or evidence updates.

### B.3 Post-writing checklist [MUST]

Before declaring a chapter ready for review, Claude MUST:

1. Run frontmatter validation (the project's `scripts/validate_frontmatter.py` if available; otherwise mental check against `_TEMPLATE.md`).
2. Re-read the chapter end-to-end once. Specifically check: any sentence containing a number ("5 weeks," "¥25,000," "10 instances") is traceable to `gcp-verified-facts.md` or a cited source.
3. Check the changelog at the bottom: a new version entry exists, dated today, summarizing the change.
4. If the chapter cites another chapter (e.g., Pattern 02 references Pattern 01), verify the cited chapter exists and the reference is accurate.

### B.4 Status promotion [SHOULD]

Chapters move through statuses: `draft` → `stable` → (rarely) `withdrawn` or `superseded`. Promotion from `draft` to `stable` SHOULD require:

- 30 days minimum since first publication, OR independent review by someone other than the author.
- No outstanding `[CONFIRM]` markers or `TODO` comments in the file.
- At least one live deployment confirmed in the Real Deployments section.

---

## C. Fact-verification procedure

**Audience: Claude in `fact-verification` mode, or any session producing a factual claim about Sugukuru's deployment.**

### C.1 The truth precedence rule [MUST]

When sources disagree, the order of precedence is:

1. **Live GCP Console / `gcloud` output** (highest)
2. **Cloud Run service YAML (most recent revision)**
3. **Cloud Logging entries (timestamp-bounded)**
4. **GCP Billing console (current month MTD or last full invoice)**
5. **Source code (HEAD of main, with file path and line number)**
6. **`gcp-verified-facts.md` in project knowledge**
7. **Cookbook chapters as currently published**
8. **Past Claude session output**
9. **Project memos**
10. **Human recollection** (lowest, due to "memos lie, YAML doesn't" — humans included)

Claude MUST cite the precedence level it relied on for any factual claim. Phrasing such as "verified via `gcloud run services describe sugukuru-core --format=yaml`, line 42" is the target standard.

### C.2 The "memos lie, YAML doesn't" rule [MUST]

Claude MUST NOT carry forward factual claims from project memos, prior session output, or human recollection without re-verification when the claim is consequential to a published chapter.

The Memorystore Redis incident of April 2026 (where a project memo's false claim of Redis usage propagated through multiple Claude sessions until reconciled with GCP Console state) is the canonical example. See `memo-errata.md`.

Re-verification means consulting at least one source above level 6 in the precedence list.

### C.3 Discovered discrepancies [MUST]

When Claude discovers that a claim in project knowledge or a published chapter contradicts higher-precedence evidence, Claude MUST:

1. Note the discrepancy explicitly in its response (do not silently correct).
2. Update `memo-errata.md` with the false claim, the verified truth, and the source.
3. Identify the chapters affected.
4. Propose corrections via the chapter changelog rather than retroactively editing.

### C.4 Uncertainty disclosure [SHOULD]

For claims that cannot be verified from a source above level 6, Claude SHOULD use one of:

- "approximately"
- "observed in live operation but not formally measured"
- "reported via human recollection; not independently verified"
- "estimated from related metrics"

Claude SHOULD NOT use these phrases when verification IS available; they are not a substitute for doing the verification.

---

## D. Knowledge-update procedure

**Audience: Claude or human, when new facts are discovered.**

### D.1 Trigger conditions [SHOULD]

A knowledge-update procedure SHOULD be initiated when:

- A new GCP configuration is observed (revision rollout, env var change, scaling annotation change).
- A new MCP spec version is released.
- A new SDK version with breaking changes is adopted.
- A new MCP server is added to or removed from the fleet.
- A discrepancy is found per C.3.

### D.2 The update sequence [MUST]

When the trigger fires, the operator (Claude or human) MUST:

1. Verify the new fact per the Section C precedence rules.
2. Update the relevant `gcp-verified-facts.md` entry (or create one).
3. List affected chapters and case studies.
4. Update each affected file with a changelog entry — do not silently edit.
5. If the update originated from a Sugukuru deployment change, note the change date and trigger ("manual scaling adjustment on YYYY-MM-DD," "deployment of new feature X").

### D.3 Truth ledger maintenance [SHOULD]

`gcp-verified-facts.md` SHOULD be re-anchored to live GCP state at least once per quarter. The procedure: select 5 entries at random, re-verify against current GCP state, note any drift in `memo-errata.md`. This catches silent infrastructure drift before it causes the next "memos lie" incident.

---

## E. Antigravity / Claude Code interoperation

**Audience: human operator coordinating between tools, and Claude in any tool.**

### E.1 Handoff in [MUST]

When work moves from Claude Projects → Antigravity (or any tool with broader codebase access), the operator MUST:

1. Export the relevant project-knowledge files (or summarize them in a single handoff bundle).
2. Include `OPERATIONS.md` in the handoff. The destination tool's Claude is bound by the same procedures.
3. Identify which specific question or task the destination tool is being asked to perform; do not delegate "make the cookbook better" — delegate "verify whether `sugukuru-core` actually runs Python or TypeScript by inspecting the Dockerfile and `package.json`/`pyproject.toml`."

### E.2 Handoff out [MUST]

When work returns from Antigravity → Claude Projects (or any review step), Claude in the receiving tool MUST:

1. Spot-verify at least one factual claim from the inbound work against a precedence-level-1-or-2 source.
2. Note any claim that conflicts with `gcp-verified-facts.md`.
3. Treat inbound chapters as `draft` regardless of how they were marked, until B.4 is satisfied.

### E.3 Conflict resolution [SHOULD]

When two tools produce conflicting work (e.g., Claude Projects and Antigravity both authored Pattern 01 and they differ), the operator SHOULD:

1. Identify which version was based on higher-precedence evidence per C.1.
2. Adopt that as the base.
3. Cherry-pick non-conflicting improvements from the other version.
4. Record the resolution in `memo-errata.md` if either version contained a verified-incorrect claim.

The goal is not consensus between Claude instances; it is alignment with verified truth.

---

# Part II — Reference

## F. Why these procedures exist

### F.1 The Memorystore incident

In April 2026, a project handoff memo claimed that Sugukuru's MCP fleet had migrated from a "Path A" single-instance configuration to a "Path B" externalized session state implementation using Memorystore Redis, with the migration triggered by CPU saturation at approximately 12 sustained concurrent sessions.

Every clause of that claim was false:
- No Memorystore Redis instance existed in the project (the API was not even enabled).
- No migration had occurred; the current configuration was the initial configuration.
- The "12 sustained sessions" threshold was not measured; it was invented during a writing pass.

The false claims propagated through three Claude sessions before being caught when the operator reconciled the memo against `gcloud run services describe` output and the GCP Billing console.

The reconciliation revealed a different and more interesting truth: Sugukuru runs `sessionAffinity: "true"` with `min-instances: 1` on the critical service and `min-instances: 0` on secondary services, with no external session store. This configuration deserved its own pattern (Path B, in v0.3 of Pattern 01), but the cookbook had been about to publish a chapter saying the opposite.

The cost of recovery: one repository teardown and rebuild, several Claude sessions of correction work, and a permanent dent in this operator's confidence in memo-based knowledge transfer.

The procedures in Part I exist to make this incident a one-time event.

### F.2 Why "stricter than necessary"

Several procedures in Part I are stricter than the day-to-day cost would seem to justify. Specifically:
- C.2 forbidding memo-based factual claims is harsher than "be a bit careful with memos."
- B.3 requiring re-reading every numerical claim in a chapter before publication is more time than a 1,500-word chapter seems to need.
- E.2 requiring spot-verification of inbound work introduces friction in the Claude Projects ↔ Antigravity loop.

The strictness is intentional. The Cookbook's primary value to its readers — regulated-domain MCP operators who will base architectural decisions on its claims — is *reliability*. A single high-profile false claim ruins that. The marginal cost per chapter of these procedures is small; the cost of a single propagated falsehood is large.

A useful frame: the procedures are calibrated such that following them feels mildly annoying. If they ever feel comfortable, they have probably been weakened, and the next Memorystore incident is approaching.

### F.3 The MUST / SHOULD / MAY split

Procedures use MUST when:
- Violating them creates a defect that affects the public cookbook (B.2 word limit, B.3 changelog entry).
- The procedure addresses a specific past failure (C.2 about memos).
- Skipping creates compounding risk (A.1 about session-start orientation).

Procedures use SHOULD when:
- The procedure is the strong default but reasonable contexts exist for deviation (A.2 about spec orientation — sometimes Claude is doing pure copy-editing where spec orientation is overhead).
- The cost of strictness exceeds the benefit for low-stakes cases (B.4 status promotion timing).

Procedures use MAY when:
- The procedure is helpful but not necessary, and the operator's discretion is trusted (A.4 tool discovery).

When in doubt about which level to apply to a new procedure, default to SHOULD. SHOULD with documented exceptions is more sustainable than MUST that gets routinely violated.

### F.4 The single-operator caveat

This project currently has one human operator. Several procedures (E.3 conflict resolution, B.4 independent review for status promotion) anticipate multi-operator workflows that do not yet exist.

This is intentional. The procedures are written so that adding a second operator does not require rewriting Part I. They are also written so that the single operator can simulate the multi-operator workflow when useful (e.g., review a chapter as a separate session before promoting it from `draft` to `stable`).

When a second operator joins, the relevant section to update first is the `audience` field at the top of this file. The procedures themselves should already work.

---

## G. Glossary of references

- **GCP**: Google Cloud Platform.
- **Cloud Run**: Google's managed serverless container platform; the deployment target for all Sugukuru MCP servers.
- **MCP**: Model Context Protocol; the protocol this cookbook is about.
- **MCP fleet**: the set of MCP servers an organization runs (for Sugukuru, currently `sugukuru-core`, `sugukuru-finance`, `sugukuru-crm`, plus `sugukuru-comms` whose membership is under verification, plus the supporting REST `sugukuru-hub`).
- **Pattern**: a reusable design solution document under `docs/patterns/`.
- **Case Study**: a documented live deployment under `docs/case-studies/`.
- **Spec**: the MCP specification, current dated 2025-11-25.
- **SEP**: Specification Enhancement Proposal; the formal proposal mechanism for changes to the spec.
- **WG / IG**: Working Group / Interest Group within the MCP community.

- **Antigravity**: Google's agent-first IDE used for codebase-wide investigation tasks.
- **Path A / B / C**: see Pattern 01.

## H. Document metadata

- This file's status MUST be `living` (continuously updated as the project evolves).
- Substantive changes (adding/removing a procedure, changing MUST→SHOULD or vice versa) MUST be reflected in the version field per semver, and MUST be logged in the changelog below.
- The file's `last_reviewed` field SHOULD be updated at least quarterly even if no changes are made, signaling that the procedures have been re-examined for continued fitness.

## I. Changelog

- **0.1.0** (2026-04-28) — Initial publication. Defines Section A (session-start), B (chapter-authoring), C (fact-verification), D (knowledge-update), E (Antigravity / Claude Code interoperation). Reference material in Part II covers the Memorystore incident as the originating motivation.
