---
title: "MCP Tools for Document OCR and Structured Extraction"
status: draft
version: 0.1.0
last_reviewed: 2026-04-27
spec_version: "2025-11-25"
domains:
  - immigration
  - finance
  - labor
  - healthcare
platforms_tested:
  - "Google Cloud Document AI"
  - "Google Cloud Run"
contributors:
  - "@sugukurukabe (Sugukuru Inc., CEO/CTO) — primary deployment"
---

# Pattern 03: MCP Tools for Document OCR and Structured Extraction

> **One-sentence summary.** Expose Cloud Document AI capabilities as MCP tools, handling file ingestion and structured schema extraction while incorporating LLM fallback for unrecognized document types.

## When to use this pattern

You are likely in scope if:

- Your MCP server needs to ingest physical documents (residence cards, passports, receipts, invoices) and extract structured data.
- You are operating in a regulated domain where data extraction accuracy dictates the legality of a subsequent operation (e.g., extracting a visa expiration date).
- You want to bridge the gap between text-native MCP interactions and binary file uploads without breaking the agent loop.

## Forces

- **Deterministic OCR vs Probabilistic LLMs.** Purpose-built OCR processors (like Document AI's Invoice or ID Parser) are more deterministic and auditable for structured extraction than passing raw images to a multimodal LLM.
- **Latency vs User Experience.** High-accuracy OCR API calls can take 10-30 seconds. In an agentic loop, this latency must be handled without timing out the MCP client transport.
- **File handling in a text protocol.** MCP is a text-based protocol. Binary images or PDFs must be ingested via base64 encoded payloads or signed URLs before processing.

## Solution

**The recommendation.** Wrap document extraction behind a tool that accepts an external reference (e.g., a Google Cloud Storage URI or base64 data). Send the document to a specialized Cloud Document AI processor based on the document type. If the document type is not supported by a specialized processor, gracefully fallback to a multimodal LLM (like Gemini) with a strict output schema.

```python
# Illustrative pseudocode
@mcp.tool(name="extract_document_data")
async def extract_document_data(gcs_uri: str, document_type: str) -> dict:
    # 1. Route to specialized processor
    if document_type == "invoice":
        processor_id = os.environ["DOCUMENT_AI_PROCESSOR_INVOICE_ID"]
        result = await call_document_ai(processor_id, gcs_uri)
    elif document_type == "id_card":
        processor_id = os.environ["DOCUMENT_AI_PROCESSOR_OCR_ID"]
        result = await call_document_ai(processor_id, gcs_uri)
    else:
        # 2. Fallback to Gemini for custom extraction
        if os.environ.get("DOCUMENT_AI_USE_FALLBACK_GEMINI") == "true":
            result = await call_gemini_extraction(gcs_uri, document_type)
        else:
            raise ValueError("Unsupported document type")
            
    # 3. Return structured schema
    return {"status": "success", "extracted_data": result}
```

## Trade-offs

- **Operational cost.** Maintaining and updating specialized processor versions in Document AI requires active monitoring.
- **Performance cost.** Synchronous OCR processing blocks the tool execution. If processing exceeds 60 seconds, it may risk transport timeouts.

## When this pattern fails

- **Failure mode: Client timeout on large files.** If the OCR process takes longer than the MCP client's timeout window, the agent receives an error despite successful background processing. Mitigation: For large batch jobs, use an asynchronous pattern that returns a job ID.

## Real deployments

- [**Case Study 01: Sugukuru Inc.**](../case-studies/01-sugukuru.md) — The `sugukuru-core` server utilizes this pattern via Document AI (`DOCUMENT_AI_ENABLED=true`). It routes ID cards and invoices to specialized processors (`DOCUMENT_AI_PROCESSOR_OCR_ID`, `DOCUMENT_AI_PROCESSOR_INVOICE_ID`) while explicitly maintaining a Gemini fallback flag (`DOCUMENT_AI_USE_FALLBACK_GEMINI=true`) for edge cases.
