---
name: run-local-github-mode
description: >
  Starts the Zava AI Agent Platform locally using GitHub Models as the inference
  provider (free, no Azure required). Suitable for Labs 0–2 and quick demos.
  Requires only a GitHub personal access token with models:read scope.
---

# Skill: run-local-github-mode

Run the full Zava AI Agent Platform locally with **zero Azure cost** by using
GitHub Models as the inference backend. All data is served from the `data/`
seed files — no Cosmos DB or PostgreSQL needed.

## Prerequisites

1. A GitHub account with access to [GitHub Models](https://github.com/marketplace/models)
2. A GitHub PAT with **`models:read`** scope:
   - Settings → Developer settings → Personal access tokens (classic) → New token
   - Scopes: ✅ `models:read`
3. Node.js ≥ 20 (for the MCP server) and Python 3.12 **or** .NET 9 SDK

## Step 1 — Create `.env`

```bash
cp .env.example .env  # if provided, else create manually
```

```dotenv
# .env — git-ignored; never commit this file

# Inference provider — GitHub Models (free)
INFERENCE_PROVIDER=github
EMBEDDINGS_PROVIDER=github

# GitHub Models endpoint (verify current URL at https://github.com/marketplace/models)
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
GITHUB_MODELS_ENDPOINT=https://models.github.ai/inference
GITHUB_MODELS_CHAT_MODEL=openai/gpt-4o-mini
GITHUB_MODELS_EMBEDDING_MODEL=openai/text-embedding-3-small
```

## Step 2 — Start the MCP server

```bash
cd src/mcp-zava
npm install
npm start          # STDIO mode (VS Code picks it up via mcp.json)
# OR
npm run start:http # HTTP/SSE on port 3000 (for direct API calls)
```

## Step 3a — Python track

```bash
cd src/python
python -m pip install -e ".[dev]"   # first time only
python -m uvicorn app.main:app --reload --port 8000
```

The server reads `.env` automatically via `python-dotenv`.

## Step 3b — .NET track

```bash
cd src/dotnet
dotnet run --launch-profile "Local"
```

Configure `appsettings.Development.json` or set env vars matching the `.env` file.

## Step 4 — Verify

```bash
# Health
curl http://localhost:8000/health       # Python
curl http://localhost:8080/health       # .NET

# List agents
curl http://localhost:8000/agents

# Chat with the concierge agent
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "What is your return policy for smart garments?",
    "agent": "concierge"
  }'
```

## Switching to Azure

When ready to use Azure resources, update `.env`:

```dotenv
INFERENCE_PROVIDER=foundry
EMBEDDINGS_PROVIDER=foundry
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://<proj>.services.ai.azure.com/api/projects/<name>
AZURE_AI_FOUNDRY_CHAT_DEPLOYMENT=gpt-4o-mini
```

Then run `azd up` to provision Azure resources and `npm run seed-data` to
populate them (see the `seed-data` skill).

## Troubleshooting

| Error | Fix |
|-------|-----|
| `401 Unauthorized` | Check `GITHUB_TOKEN` has `models:read` scope; verify token not expired |
| `Model not found` | Verify `GITHUB_MODELS_CHAT_MODEL` value against [GitHub Models catalog](https://github.com/marketplace/models) |
| `Module not found: agent-framework` | Run `pip install -e ".[dev]"` from `src/python/` |
| MCP tools not showing in Copilot | Reload VS Code after editing `mcp.json`; check Output → Copilot for errors |
