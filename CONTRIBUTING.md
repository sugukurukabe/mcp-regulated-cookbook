# Contributing

Thanks for considering a contribution. This document describes how patterns and case studies enter the cookbook, and the standards they need to meet.

## What we accept

We accept three things:

1. **Patterns** — reusable solutions to recurring problems running MCP servers in regulated domains. A pattern documents the problem, the forces involved, the solution, the trade-offs, and at least one real deployment that uses it.
2. **Case studies** — descriptions of a specific deployment, attributed or anonymized. A case study can validate an existing pattern or motivate a new one. It does not have to recommend anything.
3. **Reference material** — glossaries, decision trees, checklists. This material must be cited from at least one pattern; we do not collect reference content for its own sake.

We do not accept:
- "Hello world" or onboarding tutorials.
- Patterns derived only from blog posts, conference talks, or LLM-generated content.
- Vendor marketing material.

## How a pattern enters the cookbook

```
Issue (Pattern Proposal) → Discussion → Draft PR → Review → Merge as `draft` → Field validation → Promotion to `stable`
```

### Review Standards
Patterns are reviewed against:
- **Concreteness**: A reader should be able to tell within thirty seconds whether their situation matches the pattern.
- **Falsifiability**: The pattern must say when it is the wrong answer.
- **Production grounding**: At least one real deployment.
- **Spec correctness**: Citations to the MCP specification must be accurate.

## Case study attribution

- **Attributed**: The deploying organization is named.
- **Industry-attributed**: The industry and rough scale are named, but not the organization.
- **Anonymized**: Only the technical and regulatory shape of the deployment.
