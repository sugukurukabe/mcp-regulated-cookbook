---
title: "Tool Annotations for Regulated Operations"
status: draft
version: 0.1.1
last_reviewed: 2026-04-27
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

> **One-sentence summary.** Choose `destructive`, `idempotent`, `read-only`, and `open-world` annotations based on the legal effect of the tool, not on whether the operation feels reversible to the engineer writing it.

## When to use this pattern

You are likely in scope if:

- A tool in your MCP server, when called incorrectly, can cause a reportable incident under a regulator's definition — a missed filing deadline, an unauthorized disclosure, a transaction that cannot be reversed without paperwork.
- Your tools are exposed to MCP clients where the client uses annotations to decide whether to ask for user confirmation.

You are likely **not** in scope if:

- Your tools all read public data and you have no write paths.
- Your domain has no concept of irreversibility.

## Forces

- **Engineer intuition vs legal effect.** "It writes to a database, but I can DELETE the row tomorrow" feels reversible to the engineer. To the regulator, it is a record-keeping event that has already occurred and cannot be unwritten.
- **Client UX vs safety.** Marking too many tools as `destructive` trains users to click through confirmation dialogs reflexively. 

## Solution

**The recommendation in one paragraph.** Treat `destructiveHint` as a property of the *real-world consequence*, not the *technical operation*. If "undo it" requires anything outside the system — a phone call, a paper form, a notification to a regulator — the tool is `destructive: true`. 

### A decision procedure

**1. Is the only side effect of this tool reading data, with no write to any system of record?**
If yes: `readOnlyHint: true`. Set `destructiveHint: false`, `idempotentHint: true`. 

**2. If this tool were called incorrectly once, would undoing it require any human action that is not a reverse-tool-call in this same MCP server?**
If yes: `destructiveHint: true`. 

**3. If this tool is called twice with identical inputs, will the second call produce the same observable outcome as the first?**
If yes: `idempotentHint: true`.

**4. Does this tool act on data drawn from sources outside your control?**
If yes: `openWorldHint: true`. Combined with `destructiveHint: true`, this is the strongest possible signal to clients that user confirmation should be requested.

### Worked examples from regulated domains

| Tool name (illustrative) | `readOnly` | `destructive` | `idempotent` | `openWorld` | Reason |
|---|---|---|---|---|---|
| `lookup_corporate_number` | ✓ | false | ✓ | ✓ | Reads a public registry; no side effects. |
| `submit_application_to_immigration_bureau` | false | **true** | false | ✓ | Filing a submitted application requires withdrawal paperwork. Undo is not a tool call. |
| `record_periodic_report_filing` | false | **true** | ✓ | false | Idempotent on re-call, but the act of recording a regulatory filing is itself the reportable event. |

## When this pattern fails

- **Failure mode: a regulator changes the definition of "destructive".** A new statute or guidance document can convert what was a benign-looking tool into a reportable-event tool.
- **Failure mode: client UX undermines the annotation.** Some clients show a single "Allow this server to do anything" toggle that bypasses per-tool confirmation. 

## Real deployments

- [**Case Study 01: Sugukuru Inc.**](../case-studies/01-sugukuru.md) — The `suguvisa-mcp` TypeScript server maintains 42 tools for visa automation, extensively leveraging tool annotations. Scripts are used in CI (`audit-tool-annotations.ts`) to ensure that annotations meet the baseline regulatory awareness required by the Japanese Immigration Control Act.

## Changelog

- **0.1.1** (2026-04-27) — Corrected an incorrect claim about `sugukuru-comms` server tools. Shifted focus to the broader tool annotation practices observed in the `suguvisa-mcp` project codebase.
