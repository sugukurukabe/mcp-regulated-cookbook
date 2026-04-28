---
title: "Tool Annotations for Regulated Operations"
status: draft
version: 0.2.0
last_reviewed: 2026-04-28
spec_version: "2025-11-25"
domains:
  - immigration
  - healthcare
  - finance
  - labor
  - public-sector
platforms_tested:
  - "Anthropic Claude (claude.ai, API)"
  - "Cursor 1.x"
contributors:
  - "@sugukurukabe (Sugukuru Inc., CEO/CTO) — primary deployment"
---

# Pattern 02: Tool Annotations for Regulated Operations

> **One-sentence summary.** Choose `destructive`, `idempotent`, `readOnly`, and `openWorld` annotations based on the legal effect of the tool, not on whether the operation feels reversible to the engineer writing it.

## When to use this pattern

You are likely in scope if:

- A tool in your MCP server, when called incorrectly, can cause a reportable incident under a regulator's definition — a missed filing deadline, an unauthorized disclosure, a transaction that cannot be reversed without paperwork.
- Your tools are exposed to MCP clients where the client uses annotations to decide whether to ask for user confirmation.
- Your annotation choices will be reviewed (formally or informally) by someone who is not the original tool author — a compliance officer, an auditor, a regulator's representative, or a future reviewer at your own organization.

You are likely **not** in scope if:

- All your tools read public data and you have no write paths.
- Your domain has no concept of irreversibility.

## Forces

- **Engineer intuition vs legal effect.** "It writes to a database, but I can `DELETE` the row tomorrow" feels reversible to the engineer. To the regulator, it is a record-keeping event that has already occurred and cannot be unwritten.
- **Client UX vs safety.** Marking too many tools as `destructiveHint: true` trains users to click through confirmation dialogs reflexively. Marking too few exposes them to consequential calls without warning.
- **Per-tool annotation discipline vs per-server isolation.** A monolithic MCP server with mixed-trust tools requires careful per-tool annotations. Splitting tools into multiple servers by trust boundary (e.g., a server that handles only untrusted external input) makes those annotations service-level invariants.
- **Regulatory drift.** Statutes change. A tool that was non-destructive last year may be destructive next year because a new reporting requirement attached itself to the underlying operation.

## Solution

**The recommendation in one paragraph.** Treat `destructiveHint` as a property of the *real-world consequence*, not the *technical operation*. If "undo it" requires anything outside the system — a phone call, a paper form, a notification to a regulator — the tool is `destructiveHint: true`, regardless of whether calling it twice is technically safe. Combine with `openWorldHint` when input or downstream effect crosses an untrusted-external boundary, and isolate `openWorldHint: true` tools into their own MCP server when feasible.

### A decision procedure

**1. Is the only side effect of this tool reading data, with no write to any system of record?**
If yes: `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`. Stop.

**2. If this tool were called incorrectly once, would undoing it require any human action that is not a reverse-tool-call in this same MCP server?**
If yes: `destructiveHint: true`. Examples of human actions that count as "outside the system": withdrawal paperwork submitted to a regulator, a phone call to a banking partner, an internal incident report. Examples that do not count: calling the inverse tool in the same server.

**3. If this tool is called twice with identical inputs, will the second call produce the same observable outcome as the first?**
If yes: `idempotentHint: true`. (Note: a tool can be both `destructiveHint: true` and `idempotentHint: true` — the act of recording a regulatory filing is itself the reportable event, even if the second call is a no-op.)

**4. Does this tool act on data drawn from sources outside your control?**
If yes: `openWorldHint: true`. Combined with `destructiveHint: true`, this is the strongest possible signal to clients that user confirmation should be requested.

### Worked examples from regulated domains

| Tool name (illustrative) | `readOnly` | `destructive` | `idempotent` | `openWorld` | Reason |
|---|---|---|---|---|---|
| `lookup_corporate_number` | true | false | true | true | Reads a public registry; no side effects. |
| `submit_application_to_immigration_bureau` | false | **true** | false | true | Filing a submitted application requires withdrawal paperwork. Undo is not a tool call. |
| `record_periodic_report_filing` | false | **true** | true | false | Idempotent on re-call, but the first call is itself the reportable event. |
| `compute_payroll_for_period` | true | false | true | false | Computation only; the result is stored only when a separate `commit_payroll` tool is called. |
| `commit_payroll_for_period` | false | **true** | false | false | Triggers wage transfer. Reversal requires bank cooperation. |
| `parse_ocr_residence_card` | true | false | true | true | Reads externally-supplied image data; no side effects, but the input crosses a trust boundary. |

### Annotation discipline by server boundary

A regulated-domain MCP fleet often benefits from isolating tools by trust boundary, not by tool count. The simplest case:

- **Internal-data servers** — tools that read and write data the deploying organization controls (HR records, financial records, internal documents). Annotation discipline is per-tool and follows the decision procedure above.
- **External-input servers** — tools that ingest untrusted input (webhook receivers from third-party messaging APIs, OCR of operator-supplied images, scraping of public data). Every tool inherits `openWorldHint: true` as a service-level invariant. Tools that act on the externally-supplied data after it has been ingested may also need `destructiveHint: true`.

The advantage of the split: a code-review check that "no tool in the external-input server is missing `openWorldHint: true`" is a service-level invariant rather than a per-tool annotation discipline. A junior engineer adding a tool to the wrong server is a code-review catch; mixing trust levels inside a single server makes that mistake harder to see.

### Annotation review against statute

When the cookbook's framework above is applied to a regulated domain, the annotations should be reviewable against the statutes that define which operations have legal effect. Sugukuru's deployment uses the framework above against the Japanese Immigration Control Act and Worker Dispatch Law, with awareness of those statutes embedded in tool annotations from project inception.

A formal, documented annotation review against specific statutory provisions has not yet been published by the cookbook's first deployer; this pattern represents the framework that future review will follow. The procedure is:

1. List every tool with `destructiveHint: true`.
2. For each, identify the statutory provision (or organizational policy) that defines the operation as having legal effect.
3. Identify which provisions might change such that a tool's annotation needs to flip.
4. Review the result with someone whose role is compliance-adjacent, not engineering-adjacent.

### Enforcing annotations via CI

For larger projects, manual review of annotations is prone to human error. A best practice is to enforce annotation discipline through Continuous Integration (CI).

The companion TypeScript MCP project for Sugukuru (`suguvisa-mcp`, available at [https://github.com/sugukurukabe/suguvisa-mcp](https://github.com/sugukurukabe/suguvisa-mcp)) implements a 276-line `audit-tool-annotations.ts` script. This script runs on every GitHub Actions push and statically analyzes the codebase to ensure all tools have the required regulatory annotations. It actively scans for "regulatory verbs" in tool descriptions and throws a CI error if a tool dealing with visas, payments, or contracts lacks a `destructive` or `openWorld` annotation.

By moving the trust-boundary and annotation review into the CI pipeline, the project ensures that no tool can be merged without explicitly declaring its real-world consequences.

## Trade-offs

- **Operational discipline.** This pattern requires sustained attention. Tools added in haste under deadline pressure will skip the decision procedure and inherit defaults that may be wrong.
- **Client UX.** A correctly-annotated `destructiveHint: true` tool will trigger user confirmation in compliant clients. This is the desired safety property, but produces friction. Train users on what the confirmations mean rather than letting them learn to dismiss them.
- **Spec evolution.** The MCP specification's annotation set may grow. Annotations defined here against 2025-11-25 may not capture every distinction relevant in a future spec version.

## When this pattern fails

- **Failure mode: a regulator changes the definition of "destructive".** A new statute or guidance document can convert what was a benign-looking tool into a reportable-event tool. Mitigation: schedule a periodic re-review (annually at minimum) of all `destructiveHint` decisions against current law.
- **Failure mode: client UX undermines the annotation.** Some clients show a single "Allow this server to do anything" toggle that bypasses per-tool confirmation. The annotation is correct, but the client honors it incompletely. This pattern cannot fix client behavior; it can only ensure the server is annotated honestly. Document client-specific annotation handling in your operator runbook.
- **Failure mode: annotation drift across versions.** A tool's `destructiveHint` was correct at v1. A later refactor changed what the tool actually does. The annotation was not re-reviewed. Mitigation: include annotation review in the PR template for any tool implementation change, not only for new tools.
- **Failure mode: monolithic server makes per-tool review intractable.** When a single server has 100+ tools spanning trust levels, per-tool annotation review collapses into rubber-stamping. Mitigation: split by trust boundary as described above, accepting the operational overhead of multiple servers.

## Real deployments

- [**Case Study 01: Sugukuru Inc.**](../case-studies/01-sugukuru.md) — Sugukuru operates three MCP servers (`sugukuru-core`, `sugukuru-finance`, `sugukuru-crm`) running Python on FastMCP, with 115 unique tools across the fleet. Tool annotations have been assigned with awareness of Japanese Immigration Control Act and Worker Dispatch Law constraints from project inception. A formal documented annotation review against specific statutory provisions has not yet been published; the framework in this pattern represents how that review will be conducted. The case study illustrates the pattern's `openWorldHint: true` boundary in the planned future migration of `sugukuru-comms`. Furthermore, the companion TypeScript project (`suguvisa-mcp`) actively enforces these annotations via a dedicated CI audit script.

## Related patterns

- [Pattern 01: Cloud Run Multi-Instance Session Continuity](01-cloud-run-multi-instance.md) — A complementary operational concern. Annotation correctness assumes the server actually receives the requests it expects to; Pattern 01 handles the routing reliability.
- Pattern (proposed): Audit Log Schema for `tools/call` Provenance — extends this pattern by recording which tool was called, with which annotation, against which statutory context, for later audit.
- Pattern (proposed): Lethal Trifecta Defenses for MCP Servers — extends the `openWorldHint: true` discussion into session-taint mechanisms.

## References

- MCP Specification, [Tool annotations (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
- Simon Willison, "[The Lethal Trifecta](https://simonwillison.net/2024/Sep/4/the-lethal-trifecta/)" — the originating discussion of untrusted-input + capable-tools + private-data composition.
- Japanese Immigration Control Act (出入国管理及び難民認定法).
- Japanese Worker Dispatch Law (労働者派遣事業の適正な運営の確保及び派遣労働者の保護等に関する法律).

## Changelog

- **0.2.0** (2026-04-28) — Removed reference to a separate TypeScript MCP project that operates outside this cookbook's documented scope. Replaced the deployment example with the Sugukuru Python MCP fleet's annotation discipline. Soft-pedaled the formal-review claim per actual practice. Added "Annotation discipline by server boundary" subsection to elevate trust-boundary isolation from incidental observation to a recommended technique.
- **0.1.1** (2026-04-27) — Earlier corrections (since superseded).
- **0.1.0** (2026-04-27) — Initial draft.
