---
name: collect-evidence
description: >
  Collects and packages Module B audit evidence for the AI Applications on
  Microsoft Azure Advanced Specialization. Calls the Zava Trust agent's
  generate_evidence tool and assembles the output into docs/evidence-templates/.
  Use this skill at the end of Lab 6 (capstone).
---

# Skill: collect-evidence

Assembles the Module B evidence package by invoking the Zava MCP
`generate_evidence` tool and formatting the output for an audit submission.

## When to run

Run this at the **end of Lab 6** (Capstone + Evidence) or whenever you want
a point-in-time snapshot of your audit evidence.

## Prerequisites

- MCP server running: `cd src/mcp-zava && npm start` (STDIO) or `npm run start:http` (HTTP)
- VS Code with the Zava MCP server configured in `mcp.json`
- Completed Lab 1–6 (at minimum Lab 5 Trust & Observability for B.4.1)

## Step 1 — Generate via Copilot Chat

With the MCP server running and `@zava-evidence` agent available:

```text
@zava-evidence Generate evidence for <Your Company Name>, labs 1-6 completed
```

The agent will:

1. Call `get_customers` to retrieve customer-diversity data
2. Call `generate_evidence` with your partner name and completed labs
3. Present the structured evidence document

## Step 2 — Generate via API (automated)

```bash
# Via the Python track API
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Generate Module B evidence for Contoso, all labs completed",
    "agent": "trust"
  }'

# Via the MCP server directly (requires a running HTTP server)
curl -X POST http://localhost:3000/messages?sessionId=<id> \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "generate_evidence",
      "arguments": {
        "partnerName": "Contoso",
        "controls": ["B.1.1","B.2.1","B.2.2","B.3.1","B.4.1","B.4.2"],
        "solutionTitle": "Zava AI Agent Platform",
        "labsCompleted": ["Lab 1","Lab 2","Lab 3","Lab 4","Lab 5","Lab 6"]
      }
    }
  }'
```

## Step 3 — Save and review

1. Copy the Markdown output into `docs/evidence-templates/module-b-evidence.md`
   (create the directory if it doesn't exist yet — it's owned by WS6).
2. Review each section:
   - Fill in partner-specific revenue figures for B.2.1
   - Add certified staff names and exam IDs for B.3.1
   - Attach lab output screenshots / git log snippets for B.1.1
3. Export the Markdown to PDF or Word for formal submission.

## Evidence artefacts checklist

| Control | Artefact | Where |
|---------|----------|-------|
| B.1.1 | Architecture diagram | `docs/architecture.md` |
| B.1.1 | Source code (deployed app) | This repository |
| B.1.1 | Capability statement | `docs/evidence-templates/capability-statement.md` |
| B.2.1 | ACR pillar worksheet | Partner Center export + `docs/evidence-templates/acr-worksheet.md` |
| B.2.2 | Customer diversity table | `data/customers.json` → evidence doc |
| B.3.1 | Cert crosswalk + staff roster | `docs/cert-crosswalk.md` + staff names |
| B.4.1 | Evidence index | `docs/evidence-templates/evidence-index.md` |
| B.4.2 | Onboarding/delivery templates | `docs/evidence-templates/` |

## Automating collection in CI

Add a step to your GitHub Actions workflow to regenerate evidence on each main branch push:

```yaml
- name: Generate Module B evidence
  run: |
    cd src/mcp-zava
    npm install && npm run build
    node smoke-test.mjs   # verify server is healthy first
    # TODO: add evidence export step when trust agent is deployed
```

## Related skills

- [`seed-data`](.github/skills/seed-data.md) — populate Azure backends first
- [`run-local-github-mode`](.github/skills/run-local-github-mode.md) — run locally
