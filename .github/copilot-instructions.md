# GitHub Copilot — Repository Instructions

This repository is the **Zava AI MicroHack**: a 1-day, Train-the-Trainer course that teaches
partners to build a multi-agent AI application on **Microsoft Azure** using the **Microsoft Agent
Framework**, while producing audit evidence for the *AI Applications on Microsoft Azure* Advanced
Specialization (**Module B**, controls B.1.1–B.4.2).

## Context you should always load

- **`.microhack/build-contract.md`** — the authoritative build spec (paths, env vars, HTTP API,
  agents, Azure resources, coding standards). Conform to it.
- **`docs/module-b-mapping.md`** — how lab work maps to audit controls.

## The product

- Scenario company: **Zava** (intelligent athletic apparel retailer).
- Agents: `concierge`, `merchandiser`, `operations`, `trust`, `orchestrator` — same in both tracks.
- Two tracks, identical behaviour & HTTP API: **Python** (`src/python`, FastAPI + `agent-framework`)
  and **.NET** (`src/dotnet`, Minimal API + `Microsoft.Agents.AI`).
- Custom **Zava MCP server** in `src/mcp-zava`.

## Non-negotiable standards

- **Modular inference**: chat + embeddings work on **GitHub Models** (default, free), **Azure
  OpenAI**, or **Azure AI Foundry**, selected by `INFERENCE_PROVIDER` / `EMBEDDINGS_PROVIDER`. No
  image generation. Never hardcode a provider.
- **Auth**: `DefaultAzureCredential` / **Managed Identity** for all Azure calls. **No API keys, no
  secrets in code.** Local secrets via `.env` (git-ignored); cloud secrets via Key Vault.
- **Security & deps**: use the **latest stable** package versions; keep **zero known
  vulnerabilities** (`pip-audit`, `bandit`, `dotnet list package --vulnerable`, `npm audit`). Only
  **OSS / no-paid-license** libraries — if none fits, build it.
- **IaC**: Bicep (Azure Verified Modules) under `infra/`, deployed with **azd**. Latest API
  versions. Key Vault purge protection ON; ACR anonymous pull OFF; Cosmos/Storage key-auth OFF.
- **Observability**: OpenTelemetry → Application Insights; return a `traceId` from the API.
- **Quality**: `ruff` + `mypy` + `pytest` (Python); analyzers + `dotnet format` + nullable + `xUnit`
  (.NET); `markdownlint` for docs. `.editorconfig` is authoritative.

## When generating Azure or AI code

1. Call the Azure **AI app best practices** tool (`get_azure_bestpractices_ai_app`) first.
2. Prefer the **Microsoft Agent Framework** patterns (`AIProjectClient` → agent) over legacy SDKs.
3. Verify current APIs/models via Microsoft Learn docs / MCP — do not guess versions.

## Conventions

- Keep both tracks behaviourally identical; if you change the API, change both + the contract.
- Every `src/*` directory has a README covering **GitHub-Models** and **Azure** run modes.
- Write educational, well-commented code — learners read it.
