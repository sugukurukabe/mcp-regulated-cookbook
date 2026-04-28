# Patterns Index

Reusable solutions for running MCP servers in regulated business domains. Each pattern is grounded in at least one live deployment.

## Status legend

- **stable**: validated by at least one live deployment, plus either independent review or a 30+ day quiet period after first publication. Safe to apply.
- **draft**: published, but not yet field-validated or independently reviewed. Useful but treat with appropriate skepticism.
- **proposed**: an idea that has been discussed but not yet drafted as a chapter. Tracked here so the same idea is not re-discussed independently.
- **withdrawn** or **superseded**: the pattern no longer represents current cookbook recommendation. The chapter is retained for archival reference.

## Published patterns

| # | Title | Status | Spec version | Domains |
|---|---|---|---|---|
| [01](01-cloud-run-multi-instance.md) | Cloud Run Multi-Instance Session Continuity | stable | 2025-11-25 | immigration, labor, agriculture, other |
| [02](02-tool-annotations-regulated.md) | Tool Annotations for Regulated Operations | draft | 2025-11-25 | immigration, healthcare, finance, labor, public-sector |
| [03](03-document-ocr-mcp.md) | MCP Tools for Document OCR and Structured Extraction | draft | 2025-11-25 | immigration, finance, labor, healthcare |
| [04](04-multi-tenant-mcp.md) | Multi-tenant MCP Architectures | stable | 2025-11-25 | finance, hr, healthcare, public-sector, saas |

## Proposed patterns (not yet drafted)

These are problems we believe deserve patterns, where we have not yet completed the writing or do not yet have sufficient deployment evidence. Pattern proposals are welcomed for any of these — see [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

- **Audit Log Schema for `tools/call` Provenance** — what to record per tool call so that regulator audit requests can be answered without re-deriving facts from primary system logs. Mentioned in Pattern 01 and Case Study 01 as future work.
- **Lethal Trifecta Defenses for MCP Servers** — session-taint tracking and cross-tool-trust-boundary discipline against the Lethal Trifecta pattern (untrusted input + capable tools + private data) as named by Simon Willison. Particularly relevant when a future `sugukuru-comms` MCP migration introduces untrusted external messaging.
- **Stateless HTTP Mode** — covers the alternative when your domain tolerates throwing away session state per request, and what changes when the 2026-06 MCP transport spec lands.
- **Internationalized Tool Descriptions Without Schema Drift** — keeping tool descriptions in a single language (typically English) for LLM-prompt stability while translating user-facing strings inside `outputSchema` results. See Case Study 01 §"What surprised us" for the live-operation observation.
- **Tool Versioning Under Regulatory Change** — versioning tools whose contract follows external law (e.g., when a regulator updates an annotation-relevant statute, what changes in tool registration?).


## Withdrawn / superseded patterns

None to date.

## Submitting a pattern

See [`CONTRIBUTING.md`](../../CONTRIBUTING.md) and the [Pattern Proposal issue template](../../.github/ISSUE_TEMPLATE/pattern-proposal.yml).

The shortest description of what we accept:

> A pattern is a reusable solution to a recurring problem when running an MCP server in a regulated domain, grounded in at least one live deployment whose operator participates in chapter review.
