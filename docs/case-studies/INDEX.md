# Case Studies Index

Case studies document specific live deployments. They can validate existing patterns, motivate new patterns, or simply describe a deployment shape that future readers will find useful.

## Attribution levels

Per [`cookbook-strategy-principles.md`](../../cookbook-strategy-principles.md) §5.2, case studies declare their attribution level:

- **`attributed`**: the deploying organization is named, and a contact participates in review.
- **`industry-attributed`**: industry and rough scale are named, but not the organization.
- **`anonymized`**: only the technical and regulatory shape of the deployment.

## Index

| # | Title | Attribution | Validates patterns |
|---|---|---|---|
| [01](01-sugukuru.md) | Sugukuru Inc.: Three Python MCP servers for Japanese SSW visa and labor dispatch operations | attributed | 01, 02, 04 |

## Submitting a case study

See [`CONTRIBUTING.md`](../../CONTRIBUTING.md) and the [Case Study Submission issue template](../../.github/ISSUE_TEMPLATE/case-study-submission.yml).

We particularly welcome submissions from:

- Operators in regulated domains we do not yet cover (healthcare, finance, public-sector, education).
- Operators using runtimes or platforms different from those documented in current chapters (Node.js MCP servers, AWS Lambda deployments, Azure Container Apps).
- Operators whose deployment validates a pattern that currently has only one live reference.
- Operators who can document a failure mode that we have not yet seen.

We do not require positive outcomes. A case study describing what did not work, or what was harder than expected, is as valuable as a success story.
