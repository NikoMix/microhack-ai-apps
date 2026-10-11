# Solution 5 — Trust, Safety & Observability

> **Facilitator note:** The safety block demo is always memorable. Run Step 2 live from the
> projector — the intercept pattern makes the governance architecture concrete. Students often
> ask "what threshold triggers a block?" — answer: severity score ≥ 2 on any Content Safety
> category.

## Expected command outputs

### Safe message — passes gate (Step 1)

```json
{
  "reply": "The ZP-002 Temperature-Adaptive Jacket has a removable machine-washable outer shell. The smart heating element layer and inner sensor panel should be hand-washed in cool water or placed in a mesh laundry bag on a delicate cycle. Remove the USB charging dongle before washing.",
  "agent": "concierge",
  "citations": [
    {
      "source": "data/policies/smart-garment-care.md",
      "chunk": "The ZP-002 outer shell is machine washable (30°C, delicate cycle)...",
      "score": 0.91
    }
  ],
  "traceId": "1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f"
}
```

### Unsafe message — blocked by trust agent (Step 2)

```json
{
  "reply": "I'm sorry, I can't assist with that request. Please contact Zava support if you have a product safety concern.",
  "agent": "trust",
  "citations": [],
  "traceId": "2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f1a"
}
```

_Key points to highlight:_

- `"agent": "trust"` — the trust agent intercepted, not concierge.
- The `traceId` is still populated — the trace shows the Content Safety call.
- The reply is a generic refusal — no LLM content exposed.

### Policy lookup (Step 3)

```json
{
  "reply": "Zava's AI Governance Policy (v1.2) defines three core principles: Transparency (all AI responses include a traceId), Safety (all outputs pass the Content Safety gate before delivery), and Accountability (evidence package maintained quarterly). The policy is aligned with the OWASP LLM Top 10 and Microsoft Responsible AI Standard.",
  "agent": "trust",
  "citations": [
    {
      "source": "data/policies/ai-governance.md",
      "chunk": "Zava AI Governance Policy v1.2 — Transparency, Safety, Accountability...",
      "score": 0.97
    }
  ],
  "traceId": "3e4f5a6b7c8d9e0f1a2b3c4d5e6f1a2b"
}
```

## Application Insights KQL queries (reference)

### Request latency by minute

```kql
requests
| where name contains "/chat"
| summarize avg(duration), percentile(duration, 95) by bin(timestamp, 1m)
| order by timestamp desc
```

### Trace waterfall for a specific traceId

```kql
union requests, dependencies
| where operation_Id == "1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f"
| project timestamp, itemType, name, duration, success
| order by timestamp asc
```

### Content Safety calls by outcome

```kql
dependencies
| where name contains "ContentSafety"
| summarize count() by success
```

### Error rate trend

```kql
requests
| summarize errors=countif(success==false), total=count() by bin(timestamp, 5m)
| extend errorRate = (errors * 100.0) / total
| project timestamp, errorRate
```

## generate_evidence output

```json
{
  "reply": "Evidence package generated successfully.\n\nArtifacts compiled:\n- evidence/b11-agent-transcript-lab1.txt\n- evidence/b11-rag-citations-lab2.png (placeholder)\n- evidence/b21-resource-inventory-lab3.txt\n- evidence/b21-pgvector-seed-lab2.txt\n- evidence/b22-business-unit-queries-lab4.txt\n- evidence/b41-appi-waterfall-lab5.png (placeholder)\n\nEvidence index: evidence/index.md\nCase study draft: evidence/b11-case-study.md\nAudit checklist: evidence/b41-checklist.md",
  "agent": "trust",
  "citations": [],
  "traceId": "4f5a6b7c8d9e0f1a2b3c4d5e6f1a2b3c"
}
```

## Filled evidence artifacts

### Sample evidence/index.md

```markdown
# Module B Evidence Index — Zava AI MicroHack
Generated: 2025-07-01T16:45:00Z

## B.1.1 Azure AI Implementation
- b11-agent-transcript-lab1.txt — Multi-turn concierge conversation
- b11-rag-citations-lab2.png — RAG citations from pgvector
- b11-appi-trace-lab3.png — Application Insights trace
- b11-appi-waterfall-lab5.png — Full trace waterfall

## B.2.1 ACR Performance
- b21-resource-inventory-lab3.txt — All 3 pillars deployed
- b21-pgvector-seed-lab2.txt — Data pillar: pgvector 1536-dim
- b21-cosmos-trace-lab4.png — Cosmos DB dependency trace

## B.2.2 Customer Diversity
- b22-business-unit-queries-lab4.txt — 3 Zava business units

## B.3.1 Certifications
- b31-environment-screenshot.png — Toolchain verification

## B.4.1 Audit Readiness
- b41-appi-waterfall-lab5.png — Observability evidence
- b41-checklist.md — Pre-audit checklist

## B.4.2 Partner Onboarding
- infra/ — Bicep AVM IaC modules (reusable delivery template)
```

## Common failure modes

| Failure | Root cause | Fix |
|---------|-----------|-----|
| `generate_evidence` returns empty artifact list | Labs 1–4 artifacts not saved | Walk through the Evidence checkpoint steps in each lab |
| Content Safety not blocking | Endpoint not set or MI lacks role | Set `AZURE_CONTENTSAFETY_ENDPOINT`; verify `Cognitive Services User` |
| KQL query returns no data | Wrong workspace or time range | Extend time range to 1h; confirm App Insights name |
| Alert creation fails | Missing `Monitoring Contributor` | Assign role in Portal → Access control (IAM) |
