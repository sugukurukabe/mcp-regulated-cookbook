# Changelog

All notable changes to this cookbook are recorded here. Per-chapter changelogs live in each chapter's frontmatter; this file records repository-level changes.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), adapted for a cookbook rather than software.

## [Unreleased]

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

[Unreleased]: https://github.com/sugukurukabe/mcp-regulated-cookbook/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sugukurukabe/mcp-regulated-cookbook/releases/tag/v0.1.0
