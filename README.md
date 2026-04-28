# mcp-regulated-cookbook

> Reusable patterns for running Model Context Protocol (MCP) servers in production, particularly in regulated domains like immigration, finance, and labor.

This cookbook collects architectural patterns and case studies for deploying MCP servers in environments where safety, compliance, and auditability are as important as AI capability. 

**Core Principle**: Every pattern in this cookbook must be backed by at least one real production deployment. We do not publish purely theoretical architectures.

## What's inside

### Patterns
- [Pattern 01: Cloud Run Multi-Instance Session Continuity](docs/patterns/01-cloud-run-multi-instance.md)
- [Pattern 02: Tool Annotations for Regulated Operations](docs/patterns/02-tool-annotations-regulated.md)
- [Pattern 03: MCP Tools for Document OCR and Structured Extraction](docs/patterns/03-document-ocr-mcp.md)
- [Pattern 04: Multi-tenant MCP Architectures: Context-bound Data Isolation](docs/patterns/04-multi-tenant-mcp.md)

### Case Studies
- [Case Study 01: Sugukuru Inc.](docs/case-studies/01-sugukuru.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose a pattern or case study. We adhere to a strict "Production Grounding" rule: if it hasn't been tested in a real deployment, it cannot become a stable pattern.

## License

Apache 2.0
