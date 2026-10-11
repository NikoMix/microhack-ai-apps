# Solutions — Facilitator Answer Keys

> **⚠️ FACILITATOR-ONLY CONTENT**
> These are completed solutions, expected outputs, and filled evidence templates.
> Do not share this folder with students during a live delivery.

## Purpose

Each solution file provides:

1. **Expected commands** — exact commands the lab instructs.
2. **Sample outputs** — what a working environment produces.
3. **Filled evidence artifacts** — sample completed templates.
4. **Facilitator notes** — common failure modes and quick fixes.

## Lab solutions

| Solution | Lab | Est. time |
|----------|-----|----------:|
| [Solution 0](solution0.md) | Lab 0 — Setup & prerequisites | 20 min |
| [Solution 1](solution1.md) | Lab 1 — First Zava agent | 50 min |
| [Solution 2](solution2.md) | Lab 2 — RAG over Zava knowledge | 50 min |
| [Solution 3](solution3.md) | Lab 3 — Deploy to Azure | 55 min |
| [Solution 4](solution4.md) | Lab 4 — Data agents | 45 min |
| [Solution 5](solution5.md) | Lab 5 — Trust & observability | 45 min |
| [Solution 6](solution6.md) | Lab 6 — Capstone + evidence | 45 min |

## Quick-reference cheat sheet

### Critical env vars

```dotenv
INFERENCE_PROVIDER=github            # or azure-openai | foundry
EMBEDDINGS_PROVIDER=github           # or azure-openai | foundry
GITHUB_TOKEN=ghp_...                 # models:read scope
GITHUB_MODELS_ENDPOINT=https://models.github.ai/inference
GITHUB_MODELS_CHAT_MODEL=openai/gpt-4o-mini
GITHUB_MODELS_EMBEDDING_MODEL=openai/text-embedding-3-small
```

### API ports

| Service | Local port |
|---------|-----------|
| api-python | 8000 |
| api-dotnet | 8080 |
| mcp-zava | 3001 |

### Key IDs from seed data

| Type | IDs |
|------|-----|
| Orders | ZO-001 … ZO-010 |
| Products | ZP-001 … ZP-010 |
| Customers | Zava Retail Stores, Zava eCommerce, Zava Wholesale |
| Suppliers | SUP-001 … SUP-003 |

### Module B control quick map

| Control | Primary lab | Evidence artifact |
|---------|------------|-------------------|
| B.1.1 | Labs 1–6 | case study, architecture, transcript |
| B.2.1 | Labs 2–4 | ACR pillar worksheet, resource inventory |
| B.2.2 | Labs 4, 6 | customer diversity table |
| B.3.1 | Labs 0–6 | cert crosswalk, study plan |
| B.4.1 | Labs 5–6 | evidence index, pre-audit checklist |
| B.4.2 | Labs 3, 6 | onboarding pack, infra IaC |

## Facilitator setup checklist

Before a live delivery, verify:

- [ ] Your own `.env` is configured with a valid `GITHUB_TOKEN`.
- [ ] `GET /health` returns `{"status": "ok"}` on both ports.
- [ ] `GET /agents` returns 5 agents.
- [ ] For Labs 3+: your Azure subscription is `az login`-authenticated; `azd` is installed.
- [ ] Slide decks in `slides/` are up to date (see Facilitator Guide).
