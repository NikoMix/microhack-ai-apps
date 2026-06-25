# Lab 1 — Your First Zava Agent (Concierge)

> **Estimated time:** 50 minutes
> **Module B controls:** B.1.1 (Azure AI Implementation), B.3.1 (Certifications)

## Learning objectives

By the end of this lab you will be able to:

1. Understand the Microsoft Agent Framework's agent + tools pattern.
2. Inspect the `concierge` agent definition, its four tools, and how it's registered.
3. Call each agent tool via the HTTP API and interpret the response.
4. Trace a multi-turn conversation using session IDs.
5. Explain the modular inference abstraction (`INFERENCE_PROVIDER`).

## Prerequisites

- Lab 0 complete — dev container running, `.env` configured, API healthy.

---

## Background — Microsoft Agent Framework

The Zava API is built on the **Microsoft Agent Framework** (Python: `agent-framework`; .NET:
`Microsoft.Agents.AI`). Each agent is:

1. A **system prompt** describing its role and persona.
2. A set of **tools** (Python functions / .NET methods) the LLM can call.
3. A **runtime** that manages the conversation loop, tool execution, and handoffs.

The `orchestrator` agent receives every `/chat` request and routes it to a specialist (e.g.
`concierge` for customer support questions).

---

## Step 1 — Explore the concierge agent definition

=== "Python"

    ```bash
    # View the agent definition
    cat src/python/app/agents/concierge.py
    ```

=== ".NET"

    ```bash
    # View the agent definition
    cat src/dotnet/Agents/ConciergeAgent.cs
    ```

The `concierge` agent exposes four tools:

| Tool | What it does |
|------|-------------|
| `get_order` | Retrieves an order by ID from Cosmos DB |
| `get_product` | Returns product details from the catalog |
| `search_knowledge` | Vector-searches Zava knowledge (RAG) |
| `create_return` | Initiates a product return |

---

## Step 2 — List agents and confirm concierge is registered

```bash
# Replace 8000 with 8080 for .NET
curl -s http://localhost:8000/agents | python -m json.tool
```

Expected (abbreviated):

```json
[
  { "key": "concierge",    "name": "Zava Concierge",    "description": "Customer support..." },
  { "key": "merchandiser", "name": "Zava Merchandiser",  "description": "Product insights..." },
  { "key": "operations",   "name": "Zava Operations",   "description": "Supply chain..." },
  { "key": "trust",        "name": "Zava Trust",        "description": "Governance..." },
  { "key": "orchestrator", "name": "Zava Orchestrator", "description": "Triage and route..." }
]
```

---

## Step 3 — Chat with the concierge directly

Use the `agent` field to bypass the orchestrator and talk to the concierge directly:

=== "Python"

    ```bash
    curl -s -X POST http://localhost:8000/chat \
      -H "Content-Type: application/json" \
      -d '{
        "message": "What is the status of order ZO-001?",
        "agent": "concierge"
      }' | python -m json.tool
    ```

=== ".NET"

    ```bash
    curl -s -X POST http://localhost:8080/chat \
      -H "Content-Type: application/json" \
      -d "{
        \"message\": \"What is the status of order ZO-001?\",
        \"agent\": \"concierge\"
      }" | python -m json.tool
    ```

Expected response:

```json
{
  "reply": "Order ZO-001 for Zava Retail Stores is currently 'shipped'...",
  "agent": "concierge",
  "citations": [],
  "traceId": "..."
}
```

!!! tip "Order IDs"
    Sample orders live in `data/orders.json`. IDs follow the pattern `ZO-001`, `ZO-002`, etc.

---

## Step 4 — Multi-turn conversation with session IDs

Send a follow-up message in the same conversation by reusing the `sessionId`:

=== "Python"

    ```bash
    # Turn 1
    SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
      -H "Content-Type: application/json" \
      -d '{
        "message": "I want to return the connected running shirt from order ZO-001.",
        "agent": "concierge",
        "sessionId": "lab1-demo"
      }')
    echo $SESSION_RESPONSE | python -m json.tool

    # Turn 2 — the agent remembers the context
    curl -s -X POST http://localhost:8000/chat \
      -H "Content-Type: application/json" \
      -d '{
        "message": "What is your return policy?",
        "agent": "concierge",
        "sessionId": "lab1-demo"
      }' | python -m json.tool
    ```

=== ".NET"

    ```bash
    curl -s -X POST http://localhost:8080/chat \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"I want to return the running shirt from ZO-001.\",
           \"agent\": \"concierge\", \"sessionId\": \"lab1-demo\"}" \
      | python -m json.tool

    curl -s -X POST http://localhost:8080/chat \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"What is your return policy?\",
           \"agent\": \"concierge\", \"sessionId\": \"lab1-demo\"}" \
      | python -m json.tool
    ```

Notice that the second response references the return context from turn 1 — the session is
maintained by the Agent Framework.

---

## Step 5 — Exercise the get_product tool

Ask about a specific product to trigger the `get_product` tool:

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about the ZP-001 smart running shirt.", "agent": "concierge"}' \
  | python -m json.tool
```

!!! tip "Product IDs"
    Products are in `data/products.json`. IDs follow the pattern `ZP-001` … `ZP-010`.

---

## Step 6 — Let the orchestrator triage

Omit the `agent` field and let the `orchestrator` decide which agent handles the request:

=== "Python"

    ```bash
    curl -s -X POST http://localhost:8000/chat \
      -H "Content-Type: application/json" \
      -d '{"message": "My order ZO-002 is late. Can you help?"}' \
      | python -m json.tool
    ```

=== ".NET"

    ```bash
    curl -s -X POST http://localhost:8080/chat \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"My order ZO-002 is late. Can you help?\"}" \
      | python -m json.tool
    ```

Observe that `"agent": "concierge"` appears in the response — the orchestrator triaged correctly.

---

## Step 7 — Explore modular inference

Open `.env` and change the provider temporarily to see how the abstraction works:

```dotenv
# Switch to Azure OpenAI (if you have it configured):
# INFERENCE_PROVIDER=azure-openai
# AZURE_OPENAI_ENDPOINT=https://YOUR_ACCOUNT.openai.azure.com
# AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
# AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

The agent behavior is identical — the provider change is transparent to the agent code.

!!! info "Default stays github"
    Leave `INFERENCE_PROVIDER=github` for the rest of Labs 1–2. You will switch to Azure in Lab 3.

---

## Validation checklist

- [ ] `GET /agents` returns exactly 5 agents, including `concierge`.
- [ ] `POST /chat` with `"agent": "concierge"` and order `ZO-001` returns the order status.
- [ ] Multi-turn conversation with `sessionId` shows context continuity.
- [ ] Orchestrator correctly routes an order question to `concierge`.
- [ ] `traceId` is present and non-empty in every response.

---

## Evidence checkpoint — B.1.1

| Artifact | What it proves | Control |
|----------|---------------|---------|
| Terminal screenshot: 5 agents listed | AI agent platform built on Agent Framework | B.1.1 |
| Chat transcript: multi-turn with sessionId | Stateful agent capability on Azure AI stack | B.1.1 |
| `traceId` visible in response | Observability instrumentation | B.1.1 |

> **Action:** Copy a multi-turn chat transcript (turns 1–2 from Step 4) to
> `evidence/b11-agent-transcript-lab1.txt`. You will package it in the capstone.

---

## Key concepts review

| Concept | Detail |
|---------|--------|
| Agent Framework | Manages LLM conversation loop + tool dispatch |
| Tool / function | Python function / .NET method the LLM can invoke |
| `sessionId` | Groups turns into one conversation context |
| `agent` field | Routes directly; omit to let orchestrator decide |
| `traceId` | OpenTelemetry trace ID — links to Application Insights |
| `INFERENCE_PROVIDER` | `github` (free) → `azure-openai` → `foundry` |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Tool call returns empty `citations` | Expected in Lab 1 — RAG is added in Lab 2 |
| `order not found` | Check ID matches `data/orders.json` (e.g. `ZO-001`) |
| Agent responds in wrong language | The LLM inherits locale from the message; send English |
| `500 Internal Server Error` | Check API logs; likely a missing env var |

## Next lab

Proceed to **[Lab 2 — Ground it: RAG over Zava knowledge](lab2.md)**.
