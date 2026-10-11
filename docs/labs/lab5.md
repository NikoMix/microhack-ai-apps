# Lab 5 — Trust, Safety & Observability

> **Estimated time:** 45 minutes
> **Module B controls:** B.1.1 (Azure AI Implementation), B.3.1 (Certifications),
> B.4.1 (Audit Readiness — evidence generation begins here)

## Learning objectives

By the end of this lab you will be able to:

1. Invoke the `trust` agent's content safety gate (`content_safety_check`).
2. Demonstrate how the `trust` agent blocks unsafe requests before they reach other agents.
3. View end-to-end distributed traces in Application Insights with custom `traceId`.
4. Set up OpenTelemetry metric alerts on response latency and error rate.
5. Run the `trust` agent's `generate_evidence` tool to produce a partial evidence package.

## Prerequisites

- Lab 4 complete — data agents working.
- Azure infrastructure running (`$PYTHON_URL` set).

---

## Background — the Trust & Compliance agent

The `trust` agent is Zava's governance layer. Every sensitive agent response passes through its
`content_safety_check` tool before being returned to the caller. It also exposes:

- `policy_lookup` — retrieves Zava governance policies from the knowledge base.
- `generate_evidence` — assembles the Module B evidence package from lab outputs.

The content safety check calls **Azure AI Content Safety** (`AZURE_CONTENTSAFETY_ENDPOINT`) and
categorises text across hate, self-harm, sexual, and violence dimensions. Unsafe content is
blocked; the API returns a 200 with a safe refusal message rather than exposing the raw LLM output.

!!! info "OWASP for AI agents"
    The safety gate pattern addresses **OWASP LLM Top 10** risks LLM01 (prompt injection),
    LLM06 (sensitive information disclosure), and LLM08 (excessive agency).

---

## Step 1 — Test the safety gate (safe message)

```bash
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Is the ZP-002 jacket machine washable?", "agent": "concierge"}' \
  | python -m json.tool
```

Expected: normal reply. The `trust` agent ran `content_safety_check` internally; all categories
scored 0 (safe).

---

## Step 2 — Test the safety gate (blocked message)

Send a message that triggers the content safety filter:

```bash
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I harm someone with the heating element in the jacket?", "agent": "concierge"}' \
  | python -m json.tool
```

Expected response:

```json
{
  "reply": "I'm sorry, I can't assist with that request. Please contact Zava support if you have a product safety concern.",
  "agent": "trust",
  "citations": [],
  "traceId": "..."
}
```

The request was intercepted by the `trust` agent before reaching the `concierge`.

!!! note "The safety intercept pattern"
    When Content Safety returns a severity score ≥ 2 on any category, the trust agent short-circuits
    the response. The `agent` field in the response is set to `"trust"` to indicate intervention.

---

## Step 3 — Policy lookup

```bash
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Zava's AI governance policy?", "agent": "trust"}' \
  | python -m json.tool
```

The `trust` agent uses `policy_lookup` to retrieve governance policies from the vector knowledge
base (same AI Search / pgvector index as the concierge, but filtered to governance documents).

---

## Step 4 — Explore distributed traces

### 4a — Retrieve a trace by ID

Take the `traceId` from the Step 1 response and look it up:

```bash
TRACE_ID="<paste your traceId here>"

# Application Insights REST API (requires az CLI)
az monitor app-insights query \
  --app appi-zava-dev \
  --resource-group rg-zava-dev \
  --analytics-query "requests | where operation_Id == '$TRACE_ID' | project timestamp, name, duration, success" \
  --output table
```

### 4b — Portal trace view

1. Open Application Insights → **Transaction search**.
2. Set time range to **Last 30 minutes**.
3. Search for your `traceId`.
4. Expand the trace waterfall. You will see:
   - `POST /chat` (API layer)
   - `orchestrator.route` (Agent Framework span)
   - `concierge.content_safety_check` (trust agent)
   - Content Safety HTTP dependency call
   - `concierge.search_knowledge` (AI Search call)
   - Cosmos DB dependency (if triggered)

### 4c — Custom dashboard

Create a simple latency chart:

```bash
az monitor app-insights query \
  --app appi-zava-dev \
  --resource-group rg-zava-dev \
  --analytics-query "requests | where name contains '/chat' | summarize avg(duration), percentile(duration,95) by bin(timestamp, 1m)" \
  --output table
```

---

## Step 5 — Set up a latency alert

```bash
az monitor metrics alert create \
  --name "ZavaChatP95Latency" \
  --resource-group rg-zava-dev \
  --scopes $(az resource show -g rg-zava-dev -n appi-zava-dev --resource-type microsoft.insights/components --query id -o tsv) \
  --condition "avg requests/duration > 2000" \
  --description "Alert when /chat P95 latency exceeds 2 seconds" \
  --window-size 5m \
  --evaluation-frequency 1m
```

---

## Step 6 — Generate partial evidence with the trust agent

The `trust` agent's `generate_evidence` tool compiles artifacts collected in Labs 1–5:

```bash
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate the Module B evidence package for labs 0 through 5.",
    "agent": "trust"
  }' | python -m json.tool
```

Expected response:

```json
{
  "reply": "Evidence package generated. Artifacts compiled: b11-agent-transcript.txt, b11-rag-citations.png, b21-resource-inventory.txt, b22-business-unit-queries.txt. Evidence index written to evidence/index.md.",
  "agent": "trust",
  "citations": [],
  "traceId": "..."
}
```

Inspect the generated index:

=== "Python"

    ```bash
    ls -la evidence/
    cat evidence/index.md
    ```

=== ".NET (PowerShell)"

    ```bash
    Get-ChildItem evidence/
    Get-Content evidence/index.md
    ```

---

## Step 7 — Review the OWASP agent security checklist

The trust agent `policy_lookup` exposes the Zava AI security policy. Ask it directly:

```bash
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List the OWASP LLM risks this platform mitigates.", "agent": "trust"}' \
  | python -m json.tool
```

Expected: the trust agent cites Zava's AI governance policy (from pgvector) mapping platform
controls to LLM01, LLM06, LLM08.

---

## Validation checklist

- [ ] Safe message passes the content safety gate with a normal reply.
- [ ] Unsafe message is blocked; `"agent": "trust"` in response.
- [ ] Application Insights trace shows the full waterfall including Content Safety call.
- [ ] KQL query returns `/chat` latency data.
- [ ] Latency alert created.
- [ ] `generate_evidence` writes `evidence/index.md` with ≥ 4 artifact entries.
- [ ] `policy_lookup` returns Zava AI governance policy citations.

---

## Evidence checkpoint — B.4.1

| Artifact | What it proves | Control |
|----------|---------------|---------|
| Blocked message screenshot | Content Safety gate in production | B.1.1 |
| Application Insights trace waterfall screenshot | Observability for audit | B.4.1 |
| `evidence/index.md` (partial) | Evidence index — audit-readiness | B.4.1 |
| Latency alert configuration | Operational governance | B.4.1 |
| OWASP risk mitigation policy | AI governance policy | B.4.1 |

> **Action:** Save the Application Insights waterfall screenshot as
> `evidence/b41-appi-waterfall-lab5.png`. The `evidence/index.md` is the seed for the full
> evidence index you complete in Lab 6.

---

## Key concepts review

| Concept | Detail |
|---------|--------|
| `content_safety_check` | Calls Azure AI Content Safety; blocks severity ≥ 2 |
| `policy_lookup` | RAG over governance policies in vector knowledge base |
| `generate_evidence` | Assembles Module B artifact package; writes `evidence/index.md` |
| OpenTelemetry `traceId` | W3C Trace Context trace ID; propagated through the agent chain |
| Application Insights | Receives OTLP telemetry; shows waterfall, KQL, alerts |
| OWASP LLM Top 10 | LLM01 (prompt injection), LLM06 (data leakage), LLM08 (agency) |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Content Safety not blocking | Check `AZURE_CONTENTSAFETY_ENDPOINT`; verify MI has `Cognitive Services User` role |
| `generate_evidence` returns empty | Run Labs 1–4 first to create the source artifacts |
| No Application Insights data | Confirm `APPLICATIONINSIGHTS_CONNECTION_STRING` is in Container App env |
| Alert creation fails | Confirm you have `Monitoring Contributor` role on the resource group |

## Next lab

Proceed to **[Lab 6 — Capstone: Extend Zava & Generate Evidence](lab6.md)**.
