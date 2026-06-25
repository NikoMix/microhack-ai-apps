# Solution 0 — Environment & GitHub Models

> **Facilitator note:** This lab rarely fails if students have Docker Desktop or Codespaces. The
> most common issue is a `GITHUB_TOKEN` with wrong scopes.

## Expected command outputs

### Tool version checks

```text
Python 3.12.3
dotnet 9.0.100
v20.18.0
azure-cli 2.60.0
azd version 1.9.5 (commit 7a2b3c4d)
markdownlint-cli 0.38.0
```

### Health check

```bash
curl -s http://localhost:8000/health | python -m json.tool
```

```json
{ "status": "ok" }
```

### Agents list

```bash
curl -s http://localhost:8000/agents | python -m json.tool
```

```json
[
  {
    "key": "concierge",
    "name": "Zava Concierge",
    "description": "Handles customer support: order status, returns, and product Q&A."
  },
  {
    "key": "merchandiser",
    "name": "Zava Merchandiser",
    "description": "Provides product insights, recommendations, and review analysis."
  },
  {
    "key": "operations",
    "name": "Zava Operations",
    "description": "Manages supply chain, inventory, and supplier document parsing."
  },
  {
    "key": "trust",
    "name": "Zava Trust & Compliance",
    "description": "Content safety, governance policy lookup, and audit evidence generation."
  },
  {
    "key": "orchestrator",
    "name": "Zava Orchestrator",
    "description": "Routes incoming requests to the appropriate specialist agent."
  }
]
```

### First chat call

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What Zava products do you sell?"}' \
  | python -m json.tool
```

```json
{
  "reply": "Zava specialises in intelligent athletic apparel. Our current catalog includes the ZP-001 Connected Running Shirt, ZP-002 Temperature-Adaptive Jacket, ZP-003 Recovery Leggings, and 7 more smart garments designed for performance athletes. Which category interests you?",
  "agent": "concierge",
  "citations": [],
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

## Filled evidence artifact

### b31-environment-screenshot.png

_Facilitator captures the terminal output of the six version checks. Sample content:_

```text
$ python --version && dotnet --version && node --version && az --version | head -1 && azd version && markdownlint --version
Python 3.12.3
9.0.100
v20.18.0
azure-cli 2.60.0
azd version 1.9.5 (commit 7a2b3c4d)
markdownlint-cli 0.38.0
```

## Common failure modes

| Failure | Root cause | Fix |
|---------|-----------|-----|
| `401 Unauthorized` from GitHub Models | Token lacks `models:read` | Regenerate with correct scope |
| `connection refused :8000` | API not started | Run `uvicorn app.main:app --port 8000` |
| `.env.example` missing | Student is on old branch | `git pull origin main` |
| Dev container won't build | Docker not running | Start Docker Desktop |
