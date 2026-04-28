# mcp-regulated-cookbook

> Production patterns for running Model Context Protocol (MCP) servers in regulated business domains.
> Apache 2.0. Maintained by [Sugukuru Inc.](https://github.com/sugukurukabe).

## What this is

A cookbook of architectural patterns and case studies for deploying MCP servers in domains where safety, compliance, and auditability matter as much as functionality — immigration, finance, labor, healthcare, public sector, education, and others.

Every pattern in this cookbook is grounded in at least one live deployment whose operator participates in chapter review. Pure-theory architectures are not published here.

> Note on the word "live": throughout this cookbook, when we describe a deployment as "live" or "in live operation", we mean it is running our own real business operations on real data — not that we have sold the system as an external product. The cookbook documents what operators run for themselves; commercial productization is out of scope.

## How to read this cookbook

If you are operating an MCP server in a regulated domain and want concrete patterns, start at [`docs/patterns/INDEX.md`](docs/patterns/INDEX.md).

If you want to see what running an MCP server in live operation looks like end-to-end, start at [`docs/case-studies/INDEX.md`](docs/case-studies/INDEX.md).

If you are considering contributing, read [`OPERATIONS.md`](OPERATIONS.md) (the operations manual), [`cookbook-strategy-principles.md`](cookbook-strategy-principles.md) (the editorial principles), and [`CONTRIBUTING.md`](CONTRIBUTING.md) (the submission flow), in that order.

## Contents

### Patterns

| # | Title | Status |
|---|---|---|
| [01](docs/patterns/01-cloud-run-multi-instance.md) | Cloud Run Multi-Instance Session Continuity | stable |
| [02](docs/patterns/02-tool-annotations-regulated.md) | Tool Annotations for Regulated Operations | draft |
| [03](docs/patterns/03-document-ocr-mcp.md) | MCP Tools for Document OCR and Structured Extraction | draft |
| [04](docs/patterns/04-multi-tenant-mcp.md) | Multi-tenant MCP Architectures | stable |

See [`docs/patterns/INDEX.md`](docs/patterns/INDEX.md) for the full index, including proposed-but-not-yet-drafted patterns.

### Case studies

| # | Title | Attribution |
|---|---|---|
| [01](docs/case-studies/01-sugukuru.md) | Sugukuru Inc.: Three Python MCP servers for Japanese SSW visa and labor dispatch operations | attributed |

See [`docs/case-studies/INDEX.md`](docs/case-studies/INDEX.md) for submission criteria.

### Operations and governance

- [`OPERATIONS.md`](OPERATIONS.md) — How sessions are run against this project. Procedures for fact-verification, chapter-authoring, and tool interoperation.
- [`cookbook-strategy-principles.md`](cookbook-strategy-principles.md) — Editorial principles. Scope rules, tone, language policy, licensing, contribution acceptance.
- [`gcp-verified-facts.md`](gcp-verified-facts.md) — The truth ledger of facts about Sugukuru's deployment that other cookbook chapters cite.
- [`memo-errata.md`](memo-errata.md) — Running record of claims this project has made that turned out to be false, with the verified truth and how they were caught.
- [`MAINTAINERS.md`](MAINTAINERS.md) — Current maintainers and how to become one.



## Spec version

The cookbook currently targets **MCP specification 2025-11-25**. Each chapter declares its target version in frontmatter. See [`cookbook-strategy-principles.md`](cookbook-strategy-principles.md) §7 for the version transition policy.

## Reporting an error

If you find a factual error in any chapter, please open an issue with the `errata` label. We treat errata seriously — see [`memo-errata.md`](memo-errata.md) for the running record. Honest correction is part of the cookbook's product.

## License

Apache 2.0 — see [`LICENSE`](LICENSE).

The cookbook's prose and code are both Apache 2.0 unless an individual chapter specifies otherwise in its frontmatter.

## Contact

Issues and pull requests via this repository. For sensitive questions (security disclosure, contribution-licensing edge cases), see [`MAINTAINERS.md`](MAINTAINERS.md).
