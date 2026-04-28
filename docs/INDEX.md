# `docs/` index

The cookbook's substantive content lives under `docs/`. Top-level operations and governance files (`OPERATIONS.md`, `cookbook-strategy-principles.md`, `gcp-verified-facts.md`, `memo-errata.md`, `MAINTAINERS.md`, `CODE_OF_CONDUCT.md`) are at the repository root.

## Subdirectories

| Path | Contents |
|---|---|
| [`patterns/`](patterns/INDEX.md) | Reusable patterns. Each pattern is one Markdown file under `patterns/NN-title.md`. |
| [`case-studies/`](case-studies/INDEX.md) | Production deployment write-ups, attributed or anonymized. |

| [`reference/`](reference/) | Glossary and other reference material. (Sparse currently.) |

## Conventions

- **English-only**: see `cookbook-strategy-principles.md` §4.
- **Spec version**: each chapter declares its target MCP spec version in frontmatter. The cookbook currently targets MCP 2025-11-25.
- **Frontmatter**: validated by `scripts/validate_frontmatter.py`. See `OPERATIONS.md` Section B.3.
- **Length**: patterns are 3,000 words or fewer; case studies are 2,500 words or fewer.
