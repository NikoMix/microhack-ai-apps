# Solution 6 — Capstone: Extend Zava & Generate Evidence

> **Facilitator note:** This is the most open-ended lab. Students who finish early can extend the
> MCP server further or write a new agent. The key deliverable is a complete `evidence/index.md`
> with entries for all six controls. Reserve the last 10 minutes for the evidence review debrief.

## Expected command outputs

### Sustainability score MCP tool (after adding the tool)

```json
{
  "productId": "ZP-001",
  "name": "Connected Running Shirt",
  "sustainabilityScore": 85,
  "rating": "Green"
}
```

### Copilot @zava-advisor response

```text
@zava-advisor What is the sustainability score for ZP-001?

[Zava Advisor]: The ZP-001 Connected Running Shirt has a sustainability score of 85/100 (Green
rating). This is based on its use of recycled polyester (rPET) and the Return-to-Recycle sensor
module programme. Would you like details on Zava's sustainability policy?
```

### Full generate_evidence output

```json
{
  "reply": "Complete Module B evidence package generated.\n\nControl coverage:\n✓ B.1.1 — 4 artifacts\n✓ B.2.1 — 3 artifacts\n✓ B.2.2 — 1 artifact\n✓ B.3.1 — 1 artifact\n✓ B.4.1 — 2 artifacts\n✓ B.4.2 — 2 artifacts\n\nAll 6 controls covered. Evidence index: evidence/index.md",
  "agent": "trust",
  "citations": [],
  "traceId": "5a6b7c8d9e0f1a2b3c4d5e6f1a2b3c4d"
}
```

## Filled evidence artifacts

### evidence/b11-case-study.md (completed)

```markdown
# Azure AI Application Case Study — Zava AI Agent Platform

**Partner name:** [Your organisation]
**Customer name:** Zava (scenario)
**Project dates:** [Start date] – [End date]
**Solution name:** Zava AI Agent Platform

## Business challenge

Zava's three business units (Retail Stores, eCommerce, Wholesale) required fast, grounded,
trustworthy AI-powered answers about orders, products, inventory, and policies — accessible
through a single governed entry point.

## Solution delivered

A multi-agent AI platform built on the Microsoft Agent Framework, hosted on Azure Container
Apps, with:
- Orchestrator routing requests to specialist agents
- Concierge agent: RAG-grounded product Q&A and order management
- Merchandiser agent: product insights and recommendation
- Operations agent: supply chain, inventory, and document intelligence
- Trust & Compliance agent: content safety, governance, and evidence generation

## Azure services used

| Pillar | Services |
|--------|---------|
| AI Services | Azure AI Foundry, Azure OpenAI (gpt-4o-mini, text-embedding-3-small), Azure AI Search, Document Intelligence, Content Safety |
| App Platform | Azure Container Apps (3 services), Azure Container Registry, API Management |
| Data | Azure Cosmos DB, Azure Database for PostgreSQL (pgvector) |

## Technical architecture

See: docs/architecture.md (Mermaid diagram)

## Business outcomes

- Retail Stores: store associates answer product and returns questions 3× faster
- eCommerce: personalised product recommendations increase average order value
- Wholesale: automated supplier document parsing reduces invoice processing time by 80%

## Compliance and security

- All services use Managed Identity (no API keys)
- Key Vault stores all secrets (purge protection enabled)
- OpenTelemetry traces → Application Insights for full observability
- Content Safety gate prevents unsafe outputs
```

### evidence/b41-checklist.md (completed)

```markdown
# Module B Pre-Audit Checklist

**Date:** 2025-07-01
**Prepared by:** [Name]
**Environment:** rg-zava-dev (Azure subscription: [ID])

## B.1.1 Azure AI Implementation
- [x] Architecture diagram matches deployed resources (docs/architecture.md)
- [x] Agents built on Microsoft Agent Framework (src/python, src/dotnet)
- [x] GitHub Models / Azure AI Foundry both work (INFERENCE_PROVIDER tested)
- [x] RAG citations returned from AI Search / pgvector
- [x] traceId present in every API response

## B.2.1 ACR Performance
- [x] AI Services pillar: Foundry, OpenAI, AI Search, Doc Intelligence, Content Safety
- [x] App Platform pillar: Container Apps, ACR, API Management
- [x] Data pillar: Cosmos DB, PostgreSQL pgvector
- [ ] Partner Center export showing $15k ACR per pillar ← complete with real revenue data

## B.2.2 Customer Diversity
- [x] Three Zava business units in Cosmos DB customers container
- [x] Each unit has distinct orders and use case
- [ ] DPOR/PAL/CSP association type documented for real customers

## B.3.1 Certifications
- [ ] List 5 certified individuals → [Name, Cert, Date] × 5

## B.4.1 Audit Readiness
- [x] Evidence index (evidence/index.md) covers all 6 controls
- [x] Application Insights traces visible (b41-appi-waterfall-lab5.png)
- [x] Latency alert configured
- [ ] Evidence bundle archived and stored securely

## B.4.2 Partner Onboarding
- [x] Bicep IaC modules in infra/ — reusable for customer delivery
- [x] Evidence templates in docs/evidence-templates/
- [ ] Delivery runbook completed with customer-specific details
```

## Common failure modes

| Failure | Root cause | Fix |
|---------|-----------|-----|
| Copilot `@zava-advisor` not appearing | `.github/agents/` not in correct branch | Check `mcp.json` references; reload VS Code window |
| MCP tool not showing in inspector | TypeScript compile error | Run `npm run build` in `src/mcp-zava` |
| `generate_evidence` missing B.2.2 | Lab 4 business-unit file not saved | Re-run the three BU queries and save output |
| Evidence archive too large | Screenshots included as raw BMP | Convert to PNG; exclude vendor directories |
