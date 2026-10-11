# Prerequisites & Environment Setup

This page covers everything that must be in place **before** attendees arrive.
The same checklist applies to the trainer.

## Attendee prerequisites

Attendees should have completed these steps **before** the day starts.
Send this list at least 3 days in advance.

### Required

- [ ] **GitHub account** with [GitHub Copilot](https://github.com/features/copilot) enabled
      (Free, Pro, Business, or Enterprise)
- [ ] **GitHub Personal Access Token** with `models:read` scope
      (needed for GitHub Models, the free inference backend)
      → <https://github.com/settings/tokens/new> → select **Models (read-only)**
- [ ] **Docker Desktop** installed and running
      (needed for the dev container)
      → <https://www.docker.com/products/docker-desktop/>
- [ ] **Visual Studio Code** with the
      [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [ ] **Repository cloned:**

      ```bash
      git clone https://github.com/NikoMix/microhack-ai-apps.git
      cd microhack-ai-apps
      ```

- [ ] **Dev container pulled** (do this before the day — the image is large):
      Open VS Code → `Dev Containers: Reopen in Container`

### Recommended (required for Labs 3+)

- [ ] **Azure subscription** — Contributor access to a resource group
      Free trial or MSDN subscription works; estimate < $5 for the day
- [ ] **Azure CLI** installed and `az login` completed:
      → <https://learn.microsoft.com/cli/azure/install-azure-cli>
- [ ] **Azure Developer CLI (`azd`)** installed:
      → <https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd>

### Optional (improves experience)

- [ ] **GitHub CLI (`gh`)** — used in Lab 6 for creating issues and PRs
- [ ] Familiarity with either Python 3.11+ or C# 12 / .NET 8

---

## Trainer-only setup

In addition to the attendee checklist above:

- [ ] Run Labs 0–2 yourself end-to-end (< 60 min) at least once before delivery
- [ ] Provision your own Azure instance with `azd up` to demo Labs 3–6 if attendees don't have subscriptions
- [ ] Have solution branch checked out in a second terminal / VS Code window as a fallback
- [ ] Export your `GITHUB_TOKEN` before the session starts

---

## Dev container environment

The dev container (`.devcontainer/`) includes:

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12 | Python track |
| .NET SDK | 8 | .NET track |
| Node.js | 20 | MCP server, npm tools |
| Azure CLI (`az`) | latest | Azure auth + resource management |
| Azure Developer CLI (`azd`) | latest | Provision + deploy via Bicep |
| Bicep CLI | latest | IaC validation |
| GitHub CLI (`gh`) | latest | GitHub operations |
| `pip-audit` | latest | Python dependency auditing |
| `ruff` | latest | Python linting + formatting |
| `mypy` | latest | Python type checking |
| `markdownlint-cli2` | latest | Markdown linting |

Opening the repo in the dev container from VS Code installs everything automatically.

---

## GitHub Models — quick test

Once the dev container is running and `GITHUB_TOKEN` is exported:

```bash
# Verify the token and endpoint work
curl https://models.github.ai/inference/chat/completions \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4o-mini",
    "messages": [{"role": "user", "content": "Say hello from Zava!"}]
  }'
```

Expected: a JSON response with `choices[0].message.content`.

---

## Azure — environment variables

When `INFERENCE_PROVIDER` is not `github`, set these before running the API:

### Azure OpenAI

```bash
export INFERENCE_PROVIDER=azure-openai
export AZURE_OPENAI_ENDPOINT=https://<account>.openai.azure.com
export AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
export AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
# Auth: az login (local) or Managed Identity (Container Apps)
```

### Azure AI Foundry (recommended)

```bash
export INFERENCE_PROVIDER=foundry
export AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://<project>.services.ai.azure.com/api/projects/<name>
export AZURE_AI_FOUNDRY_CHAT_DEPLOYMENT=gpt-4o-mini
# Auth: az login (local) or Managed Identity (Container Apps)
```

### After `azd up`

`azd` automatically writes all `AZURE_*` environment variables to the Container Apps
environment. For local development, copy them from the `.azure/<environment>/.env` file.

---

## Network & firewall checklist

If delivering in a corporate environment, confirm the following URLs are accessible:

| URL | Purpose |
|---|---|
| `https://models.github.ai` | GitHub Models inference |
| `https://ghcr.io`, `https://docker.io` | Dev container image pull |
| `https://management.azure.com` | Azure Resource Manager (azd) |
| `https://*.openai.azure.com` | Azure OpenAI |
| `https://*.services.ai.azure.com` | Azure AI Foundry |
| `https://login.microsoftonline.com` | Azure AD / Entra ID auth |
| `https://api.github.com`, `https://github.com` | Repository access |

---

## Fallback options if Azure is blocked

If corporate network blocks Azure or attendees lack subscriptions:

1. **Run entirely on GitHub Models** — Labs 0–2 complete with zero Azure
2. **Trainer demos Labs 3–6** from their own subscription while attendees observe
3. **Use GitHub Codespaces** instead of Docker Desktop if Docker is blocked:
   - Open the repo on GitHub → **Code** → **Codespaces** → **New codespace**
   - Codespaces include the dev container automatically

---

## Troubleshooting quick reference

See [Pitfalls & Fixes](pitfalls.md) for detailed solutions.

| Symptom | Quick fix |
|---|---|
| Dev container won't start | Check Docker is running; try `docker system prune` |
| `GITHUB_TOKEN` 401 error | Re-check token has `models:read` scope and is not expired |
| `azd up` fails | Check `az login` is valid; check subscription has required quotas |
| Port 8000 already in use | `lsof -i :8000` / `Get-Process` to find + kill the process |
| `pip install` fails | Check network; try `pip install --no-cache-dir -r requirements.txt` |
