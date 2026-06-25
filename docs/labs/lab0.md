# Lab 0 — Environment & GitHub Models

> **Estimated time:** 20 minutes
> **Module B controls:** B.3.1 (Certifications baseline — environment proves toolchain competency)

## Learning objectives

By the end of this lab you will be able to:

1. Open and verify the Zava dev container (or GitHub Codespace).
2. Create a GitHub Personal Access Token (PAT) with `models:read` scope.
3. Configure the `.env` file for **GitHub Models** mode.
4. Make a first inference call to confirm the setup works end-to-end.

## Prerequisites

- GitHub account with Copilot enabled.
- Docker Desktop installed **or** GitHub Codespaces access.
- Access to [GitHub Models](https://github.com/marketplace/models) (no credit card required).

---

## Step 1 — Open the dev container

=== "VS Code (local)"

    1. Clone the repository:

        ```bash
        git clone https://github.com/NikoMix/microhack-ai-apps.git
        cd microhack-ai-apps
        ```

    2. When VS Code prompts **"Reopen in Container"**, click it. If it does not prompt, open the
       Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and run:

        ```
        Dev Containers: Reopen in Container
        ```

    3. Wait for the container to build (~2 minutes on first run).

=== "GitHub Codespace"

    1. Navigate to `https://github.com/NikoMix/microhack-ai-apps`.
    2. Click **Code → Codespaces → Create codespace on main**.
    3. The devcontainer starts automatically — no local Docker required.

### Verify the container is healthy

```bash
python --version           # expects Python 3.12+
dotnet --version           # expects .NET 9+
node --version             # expects Node 20+
az --version               # expects azure-cli 2.60+
azd version                # expects azd 1.9+
markdownlint --version     # expects 0.38+
```

!!! tip "Slow first build?"
    The devcontainer pre-installs all toolchains. Subsequent opens reuse the cached image.

---

## Step 2 — Create a GitHub Models token

1. Go to [GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens](
   https://github.com/settings/tokens?type=beta).
2. Click **Generate new token**.
3. Set a descriptive name, e.g. `zava-microhack-models`.
4. Under **Permissions → Account permissions**, grant **Models** → **Read**.
5. Click **Generate token** and copy the value — it will not be shown again.

!!! warning "Scope requirement"
    The token needs the `models:read` permission. Other scopes are not required for this lab.

---

## Step 3 — Configure `.env`

Both tracks read a `.env` file at the repository root (git-ignored). Create it from the template:

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```dotenv
# ── Inference provider ───────────────────────────────────────────────
INFERENCE_PROVIDER=github
EMBEDDINGS_PROVIDER=github

# ── GitHub Models (default / free) ──────────────────────────────────
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
GITHUB_MODELS_ENDPOINT=https://models.github.ai/inference
GITHUB_MODELS_CHAT_MODEL=openai/gpt-4o-mini
GITHUB_MODELS_EMBEDDING_MODEL=openai/text-embedding-3-small
```

!!! danger "Never commit your token"
    `.env` is in `.gitignore`. Do **not** remove that entry or add the file to git.

---

## Step 4 — Start the Python API

=== "Python"

    ```bash
    cd src/python
    pip install -r requirements.txt
    python -m uvicorn app.main:app --reload --port 8000
    ```

    Wait for:

    ```
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://127.0.0.1:8000
    ```

=== ".NET"

    ```bash
    cd src/dotnet
    dotnet restore
    dotnet run --project ZavaApi -- --urls http://localhost:8080
    ```

    Wait for:

    ```
    info: Microsoft.Hosting.Lifetime[14]
          Now listening on: http://localhost:8080
    ```

---

## Step 5 — Verify the health endpoint

=== "Python (port 8000)"

    ```bash
    curl -s http://localhost:8000/health | python -m json.tool
    ```

    Expected:

    ```json
    { "status": "ok" }
    ```

=== ".NET (port 8080)"

    ```bash
    curl -s http://localhost:8080/health | python -m json.tool
    ```

    Expected:

    ```json
    { "status": "ok" }
    ```

---

## Step 6 — First inference call

Use the `/agents` endpoint to list available agents, then send your first chat message to the
orchestrator (which triages to the appropriate specialist):

=== "Python (port 8000)"

    ```bash
    # List agents
    curl -s http://localhost:8000/agents | python -m json.tool

    # First chat — orchestrator triages automatically
    curl -s -X POST http://localhost:8000/chat \
      -H "Content-Type: application/json" \
      -d '{"message": "What Zava products do you sell?"}' \
      | python -m json.tool
    ```

=== ".NET (port 8080)"

    ```bash
    curl -s http://localhost:8080/agents | python -m json.tool

    curl -s -X POST http://localhost:8080/chat \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"What Zava products do you sell?\"}" \
      | python -m json.tool
    ```

Expected response shape:

```json
{
  "reply": "Zava offers smart athletic apparel ...",
  "agent": "concierge",
  "citations": [],
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

!!! note "traceId"
    Every response carries a `traceId`. In Lab 5 you will see this trace in Application Insights.

---

## Validation checklist

- [ ] Dev container or Codespace opened without errors.
- [ ] All tool versions meet minimums (`python`, `dotnet`, `azd`, `az`, `markdownlint`).
- [ ] `.env` created with a valid `GITHUB_TOKEN` (models:read).
- [ ] `GET /health` returns `{"status": "ok"}`.
- [ ] `GET /agents` returns a JSON array with 5 agents (`concierge`, `merchandiser`,
      `operations`, `trust`, `orchestrator`).
- [ ] `POST /chat` returns a reply with a non-empty `traceId`.

---

## Evidence checkpoint — B.3.1

| Artifact | What it proves | Control |
|----------|---------------|---------|
| Screenshot: all version checks passing | Toolchain competency for the cert study plan | B.3.1 |
| `.env` created (redacted) | Ability to configure modular inference | B.3.1 |

> **Action:** Take a screenshot of the terminal with all six `--version` checks and save it as
> `evidence/b31-environment-screenshot.png`. You will reference it in the capstone (Lab 6).

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `docker: command not found` | Install Docker Desktop or use Codespaces |
| `401 Unauthorized` from GitHub Models | Check `GITHUB_TOKEN` value; token needs `models:read` |
| Port already in use | Kill the conflicting process or change `--port` |
| `.env.example` not found | Run `git pull origin main` to get the latest template |

## Next lab

Proceed to **[Lab 1 — Your first Zava agent](lab1.md)**.
