# Changelog

All notable changes to this cookbook are recorded here. Per-chapter changelogs live in each chapter's frontmatter; this file records repository-level changes.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), adapted for a cookbook rather than software.

## [Unreleased]

## [0.1.1] — 2026-04-28

### Added
- Case Study #01: new "Operator Experience" section documenting how a four-person AI-administrator team drives the MCP fleet through Cursor + Antigravity. Includes Cursor analytics (DAU 1-4, ~81% AI-authored line ratio, 2,685 agent requests over 30 days), GitHub commit cadence (93 commits / 1,293 files / 2 contributors over 30 days), GCP API surface (Google Drive 29,099 reqs, Cloud Build 26,586, Document AI 2,499 with 42% error rate honestly disclosed), Claude API token usage (5-6× month-over-month growth, 1.24M token spike on 2026-04-04), Google Workspace OAuth-app count growth (~4× across 180 days from October 2025 to April 2026, with explicit interpretation note clarifying this is NOT the same as MCP tool count), the SmartHR/Adobe receding-subscription pattern, and forward-looking note on team expansion (two engineers from Indonesia joining May 2026).
- memo-errata §13: pre-publication hypothesis verification cycle for four claims (IDE-as-UI, Recursive Bootstrapping, Two-stage Operations, Single-Operator framing). Demonstrates Lesson 7 (cookbook applies its own rules to itself) operating in practice on cookbook-internal drafts.
- gcp-verified-facts.md §1.0: explicit GCP project ID disclosure (`sugukurucorpsite`) for reader verification of Operator Experience metrics.

### Cookbook process notes
- This release is the first to integrate three independent quantitative data sources (Cursor analytics CSV, Claude API token CSV, GCP API console) plus a fourth corroborating source (Google Workspace OAuth-app count) into a single operator-experience narrative. Each source is named with its provenance so readers can verify claims against original tooling.
- Drafts authored by Claude Opus 4.7 with operator interview; codebase investigation and instrumentation gathering split between Antigravity (Gemini 3.1 Pro) and direct operator queries; final commit and push by Antigravity, who also performs a cross-source synthesis check (see commit message).

## [0.1.0] — 2026-04-28

### Added — Initial public publication

The cookbook is published with the following initial content:

**Patterns**:
- Pattern 01: Cloud Run Multi-Instance Session Continuity (`status: stable`, v0.3.x)
- Pattern 02: Tool Annotations for Regulated Operations (`status: draft`, v0.1.x)
- Pattern 03: MCP Tools for Document OCR and Structured Extraction (`status: draft`, v0.1.0)
- Pattern 04: Multi-tenant MCP Architectures (`status: stable`, v1.0.0)

**Case studies**:
- Case Study 01: Sugukuru Inc. (`attribution: attributed`)

**Operations and governance**:
- `OPERATIONS.md` (operational procedures)
- `cookbook-strategy-principles.md` (editorial principles)
- `gcp-verified-facts.md` (truth ledger)
- `memo-errata.md` (errata record, with 10 entries from pre-publication drafting and reconciliation)
- `CONTRIBUTING.md`, `MAINTAINERS.md`, `CODE_OF_CONDUCT.md`

**Tools**:
- `scripts/validate_frontmatter.py` (frontmatter validator for cookbook chapters)

### Note

The pre-publication drafting included substantial reconciliation work against the actual Sugukuru deployment state. See `memo-errata.md` for the record. The accidentally-published Japanese-language draft files (a violation of the cookbook's English-only language policy) were removed before this initial publication; the incident is documented at `memo-errata.md` §9.

A scout component (`mcp-cookbook-scout` MCP server with companion bash hook) was prepared in pre-publication drafts but removed before initial publication after recognition that it had not been implemented or deployed and would have violated the cookbook's production-grounding principle (`cookbook-strategy-principles.md` §2.1). It will be reintroduced in a future version when actually built and run. See `memo-errata.md` §12.

[Unreleased]: https://github.com/sugukurukabe/mcp-regulated-cookbook/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/sugukurukabe/mcp-regulated-cookbook/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/sugukurukabe/mcp-regulated-cookbook/releases/tag/v0.1.0
