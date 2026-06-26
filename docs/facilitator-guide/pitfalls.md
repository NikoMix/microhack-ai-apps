# Common Pitfalls & Fixes

This reference covers the most common issues encountered during delivery and how to resolve them quickly.
Keep this page open on a second monitor during lab sessions.

---

## Environment & Setup

### Dev container won't start

**Symptom:** VS Code shows "Failed to create dev container" or Docker hangs.

**Fixes:**

1. Confirm Docker Desktop is running: `docker ps` should return a header row
2. If Docker has insufficient memory, increase it in Docker Desktop → Resources (recommend ≥ 8 GB RAM)
3. Try `docker system prune --volumes` to reclaim space, then reopen the container
4. If on Windows with WSL2, restart WSL: `wsl --shutdown` then reopen VS Code

**Fallback:** Use GitHub Codespaces — open the repo on GitHub → Code → Codespaces → New codespace. The dev container configuration is applied automatically.

---

### GitHub Models 401 Unauthorized

**Symptom:** `curl` to `https://models.github.ai/inference` returns `{"error": "Unauthorized"}`.

**Fixes:**

1. Confirm the token has `models:read` scope: go to <https://github.com/settings/tokens> and check
2. Confirm the token hasn't expired — classic tokens expire; fine-grained tokens do too
3. Re-export the variable: `export GITHUB_TOKEN=<token>` (don't include angle brackets)
4. Test directly: `curl -H "Authorization: Bearer $GITHUB_TOKEN" https://models.github.ai/inference/models`

---

### Port 8000 already in use

**Symptom:** `Error: address already in use` when starting the API.

**Fix (Linux/macOS):**

```bash
lsof -i :8000 | grep LISTEN
kill -9 <PID>
```

**Fix (Windows PowerShell):**

```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

---

## Lab 0 — Environment

### `pip install` fails with network error

**Fix:** Try `pip install --no-cache-dir -r requirements.txt`. If in a corporate environment, configure the pip proxy: `pip install --proxy http://proxy:port -r requirements.txt`.

### `.NET` SDK not found in dev container

**Fix:** The dev container should include .NET 8. If not, confirm the `.devcontainer/devcontainer.json` matches the repo's current version. Run `dotnet --version` to confirm.

---

## Lab 1 — First Agent

### Agent always responds with "I don't know"

**Cause:** The tool isn't registered (missing `@tool` decorator in Python or `[AgentTool]` attribute in .NET).

**Fix:** Add the decorator/attribute and restart the API.

### `get_order` returns no results

**Cause:** The `data/orders.json` seed data isn't loaded, or the Cosmos DB emulator isn't running.

**Fix:** In local mode, the app should load from `data/orders.json` directly. Check the data loading code in the agent constructor. Confirm `ORD-001` exists in `data/orders.json`.

### `traceId` is `null` in the response

**Cause:** OpenTelemetry isn't initialised.

**Fix:** Confirm `APPLICATIONINSIGHTS_CONNECTION_STRING` is set (even a dummy value like `InstrumentationKey=00000000...` works for local development to initialise the tracer). In Lab 1, a randomly generated UUID is acceptable as a fallback `traceId`.

---

## Lab 2 — RAG

### AI Search index creation fails

**Cause 1:** `AZURE_SEARCH_ENDPOINT` isn't set or the API key/Managed Identity isn't configured.
**Fix:** For local dev, use a local pgvector setup instead. The lab guide has instructions for the pgvector path.

**Cause 2:** Vector dimension mismatch — index was created with dimension 768 but the embedding model produces 1536.
**Fix:** Delete and recreate the index with `vector(1536)`.

### `search_knowledge` returns empty results

**Cause:** The index is empty — the indexing step wasn't run.
**Fix:** Run the indexing script: `python src/python/scripts/index_knowledge.py` (or the .NET equivalent). Confirm the script outputs "Indexed N documents."

### Provider swap breaks with "model not found"

**Cause:** The Azure AI Foundry deployment name doesn't match `AZURE_AI_FOUNDRY_CHAT_DEPLOYMENT`.
**Fix:** Go to the Azure AI Foundry portal and confirm the deployment name is exactly `gpt-4o-mini`. Update the env var to match.

---

## Lab 3 — Deploy to Azure

### `azd up` fails with quota error

**Symptom:** `QuotaExceeded: The subscription does not have enough quota for the requested resource.`

**Fixes:**

1. Switch to `eastus` or `eastus2` region which has more capacity
2. If GPU quota is the issue, confirm no GPU SKUs are being provisioned (this microhack uses CPU-only Container Apps)
3. Request quota increase in the Azure portal: Subscriptions → Usage + Quotas

### `azd up` fails with "Role assignment already exists"

**Cause:** A previous run partially completed. The Managed Identity was created but the role assignment already exists.
**Fix:** Run `azd up` again — the Bicep deployment is idempotent and will skip existing assignments.

### Container App is deployed but returns 502

**Cause:** The container failed to start. Common reasons: missing env var, failed health check.
**Fix:**

1. Check Container Apps → Revisions → click the revision → Logs
2. Look for startup errors: missing `GITHUB_TOKEN` or `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT`
3. Confirm the revision is running (not provisioning)

### Application Insights traces aren't appearing

**Cause:** Ingestion lag (1–2 minutes) or the `APPLICATIONINSIGHTS_CONNECTION_STRING` isn't set in the Container App environment.
**Fix:** Wait 2 minutes and refresh. If still not appearing, check the Container App's Environment Variables and confirm `APPLICATIONINSIGHTS_CONNECTION_STRING` is present.

---

## Lab 4 — Data Agents

### Cosmos DB returns 403 Forbidden

**Cause:** The Managed Identity hasn't been assigned the Cosmos DB RBAC role, or the role hasn't propagated yet.
**Fix:** Wait 2–3 minutes for RBAC to propagate. If still failing, go to Cosmos DB → Access Control → confirm the Managed Identity has `Cosmos DB Built-in Data Contributor` role.

### Orchestrator routes everything to Concierge

**Cause:** The Orchestrator's system prompt doesn't describe Merchandiser and Operations clearly enough.
**Fix:** Update the Orchestrator system prompt to include explicit descriptions:

- "Use `merchandiser` for product insights, reviews, and sales data."
- "Use `operations` for inventory, restock, and supplier documents."

### Document Intelligence timeout

**Cause:** Content exceeds the Document Intelligence page limit for the chosen tier, or the service isn't provisioned.
**Fix:** Use the mock implementation from the lab guide (`parse_supplier_doc` returns pre-processed data). The real implementation works the same way — the mock just bypasses the API call.

---

## Lab 5 — Trust & Observability

### Content Safety 401 or 403

**Cause:** The Content Safety endpoint isn't set, or the Managed Identity doesn't have the `Cognitive Services User` role.
**Fix:**

1. Check `AZURE_CONTENTSAFETY_ENDPOINT` is set
2. Check the Managed Identity has the role: Azure portal → Content Safety resource → IAM → Role assignments

### Content Safety not available in region

**Cause:** Content Safety has limited regional availability.
**Fix:** Check [Azure region availability](https://learn.microsoft.com/azure/ai-services/content-safety/overview#region-availability) and use a supported region. `eastus` and `westeurope` are reliably available.

### OpenTelemetry spans not appearing in App Insights

**Cause:** The OTLP exporter isn't configured or the `APPLICATIONINSIGHTS_CONNECTION_STRING` uses the old format.
**Fix:** Confirm the connection string starts with `InstrumentationKey=` followed by `Endpoint=...`. The Azure Monitor OpenTelemetry exporter uses the full connection string, not just the instrumentation key.

---

## Lab 6 — Capstone

### Custom agent not appearing in Copilot Chat

**Cause:** YAML syntax error or the file isn't saved.
**Fix:** Validate the YAML with a linter (`yamllint .github/agents/zava-architect.yml`). Save and reload Copilot Chat.

### MCP server fails to start

**Cause:** Port 3100 is in use, or `npm install` wasn't run.
**Fix:**

```bash
cd src/mcp-zava
npm install
npm start
```

If port 3100 is in use, update `package.json` to use a different port and update `mcp.json`.

### `generate_evidence` returns empty sections

**Cause:** The lab wasn't completed fully — some agents or tools are missing.
**Fix:** This is expected behaviour for partial completion. The evidence structure is still valuable — attendees will see which sections are empty and understand what work remains.

---

## General tips

- **Pair programming** — if a group is stuck, have them pair with someone who's further ahead rather than waiting for you to get to them individually
- **Solution branches** — every lab has a solution in `docs/solutions/lab-XX/`. Point stuck attendees there rather than spending 10 minutes debugging per person
- **Time box** — if a lab is running 15+ min over, demo the remaining steps and move on; lab completion isn't the goal, learning the pattern is
- **Screen share** — if running virtual, have a "helper" window open with the solution branch so you can screen-share a fix quickly
