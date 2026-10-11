# B.4.2 — Partner Onboarding: Delivery Pack & Templates

> **Control:** B.4.2 Partner Onboarding
> **What auditors check:** The partner has repeatable onboarding and delivery templates that
> enable consistent AI solution delivery to customers.
> **Evidence required:** Onboarding pack, delivery runbook, reusable templates.

---

## Overview

This pack gives you everything needed to onboard a new customer to the Zava-style
AI Agent Platform pattern and deliver it in a repeatable, documented way.

### What is in this pack

| Section | Contents |
|---------|---------|
| [Customer Discovery Worksheet](#part-1) | Pre-sales questions to scope an AI platform engagement |
| [Delivery Runbook](#part-2) | Step-by-step delivery guide (mirrors Labs 0–6) |
| [Environment Setup Template](#part-3) | Repeatable `.env` + `azd env` configuration |
| [Agent Customisation Guide](#part-4) | How to adapt agents for a new customer scenario |
| [Handover Checklist](#part-5) | Go-live and post-delivery handover |
| [Evidence Collection Checklist](#part-6) | Collect Module B evidence during delivery |

---

## Part 1 — Customer Discovery Worksheet {#part-1}

Use these questions in the initial customer discovery call.

### Business context

1. What business problem are you solving with AI?
   `[PLACEHOLDER: Customer answer]`

2. Which user groups will interact with the AI platform?
   `[PLACEHOLDER: e.g. call centre agents, store associates, analysts]`

3. What are the three most important use cases in priority order?
   1. `[PLACEHOLDER]`
   2. `[PLACEHOLDER]`
   3. `[PLACEHOLDER]`

4. Are there any content safety or compliance requirements (GDPR, HIPAA, industry-specific)?
   `[PLACEHOLDER]`

### Technical context

1. What Azure services are currently in use?
   `[PLACEHOLDER: List existing services]`

2. What is the preferred AI inference model?
   `[PLACEHOLDER: gpt-4o-mini / gpt-4o / custom fine-tuned]`

3. Where does the grounding data live today?
   `[PLACEHOLDER: SharePoint / SQL / files / APIs]`

4. What are the latency and throughput requirements for AI responses?
   `[PLACEHOLDER: e.g. < 3 s P95, 100 concurrent users]`

5. Is there an existing Azure subscription with sufficient quota?
   `[PLACEHOLDER: Subscription ID if known]`

### Timeline and budget

1. Target go-live date: `[PLACEHOLDER: YYYY-MM-DD]`

2. Estimated monthly Azure budget: `[PLACEHOLDER: USD]`

3. Team available from the customer side:
   `[PLACEHOLDER: e.g. 1 cloud architect, 1 data engineer]`

---

## Part 2 — Delivery Runbook {#part-2}

This runbook mirrors the microhack labs but is structured for a real customer delivery.

### Sprint 0 — Environment & foundation (Week 1)

| Task | Owner | Acceptance criteria |
|------|-------|-------------------|
| Create repo from template | Partner | CI passes on `main` |
| Configure dev container | Partner | All version checks pass |
| Provision Azure infrastructure | Partner | `azd provision` completes; health check returns `{"status":"ok"}` |
| Configure Managed Identity | Partner | No API keys in any env var |
| Verify telemetry | Partner | `traceId` visible in Application Insights |

**Env vars to set for Sprint 0:**

```dotenv
INFERENCE_PROVIDER=foundry
EMBEDDINGS_PROVIDER=foundry
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=[from azd env get-values]
AZURE_OPENAI_ENDPOINT=[from azd env get-values]
AZURE_CLIENT_ID=[from azd env get-values]
APPLICATIONINSIGHTS_CONNECTION_STRING=[from azd env get-values]
```

### Sprint 1 — Core agents (Weeks 2–3)

| Task | Owner | Acceptance criteria |
|------|-------|-------------------|
| Implement concierge agent with customer tools | Partner | `POST /chat` returns reply + `traceId` |
| Seed customer knowledge base | Partner | `citations` non-empty on policy queries |
| Implement orchestrator routing | Partner | Correct agent in response for each intent |
| Add content safety gate | Partner | Unsafe inputs blocked; `"agent":"trust"` in response |

**Customer-specific customisations:**

- Replace `data/policies/*.md` with the customer's actual policy documents.
- Replace `data/products.json` with the customer's product catalog.
- Update agent system prompts with the customer's brand voice and domain.

### Sprint 2 — Data agents (Weeks 3–4)

| Task | Owner | Acceptance criteria |
|------|-------|-------------------|
| Seed Cosmos DB with customer data | Partner | Agents return data from Cosmos |
| Implement customer-specific tools | Partner | All tools tested with `pytest`/`xUnit` |
| Parse customer documents (Doc Intelligence) | Partner | Line items extracted correctly |
| Validate three-customer diversity | Partner | Three business units query distinctly |

### Sprint 3 — Hardening & handover (Week 5)

| Task | Owner | Acceptance criteria |
|------|-------|-------------------|
| Security review (`pip-audit`, `bandit`, `npm audit`) | Partner | Zero high/critical vulnerabilities |
| Performance test (load: 100 concurrent `/chat`) | Partner | P95 latency < 3 s |
| Set up production alerts | Partner | Latency + error-rate alerts active |
| Run `generate_evidence` | Partner | Evidence index covers all 6 controls |
| Handover training | Partner + Customer | Customer team can run `azd deploy` |

---

## Part 3 — Environment Setup Template {#part-3}

Copy this template for each new customer environment.

### `.env.customer-name` (git-ignored)

```dotenv
# ── Customer: [PLACEHOLDER: Customer name] ──────────────────────────
# Environment: [PLACEHOLDER: dev / staging / prod]
# Date created: [PLACEHOLDER: YYYY-MM-DD]

# Inference
INFERENCE_PROVIDER=foundry
EMBEDDINGS_PROVIDER=foundry

# Azure AI Foundry (from azd env get-values)
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=[PLACEHOLDER]
AZURE_OPENAI_ENDPOINT=[PLACEHOLDER]
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# Data
COSMOS_ENDPOINT=[PLACEHOLDER]
COSMOS_DATABASE=[PLACEHOLDER: e.g. zava or customer-db]
POSTGRES_HOST=[PLACEHOLDER]
POSTGRES_DB=[PLACEHOLDER]
POSTGRES_PORT=5432

# AI Services
AZURE_SEARCH_ENDPOINT=[PLACEHOLDER]
AZURE_SEARCH_INDEX=[PLACEHOLDER: e.g. customer-knowledge]
AZURE_DOCINTEL_ENDPOINT=[PLACEHOLDER]
AZURE_CONTENTSAFETY_ENDPOINT=[PLACEHOLDER]

# Platform
AZURE_CLIENT_ID=[PLACEHOLDER]
AZURE_KEY_VAULT_ENDPOINT=[PLACEHOLDER]
APPLICATIONINSIGHTS_CONNECTION_STRING=[PLACEHOLDER]
```

### azd environment creation

```bash
# Create a customer-specific azd environment
azd env new <customer-shortname>-<stage>   # e.g. fabrikam-prod

# Set customer-specific parameters (overrides bicep defaults)
azd env set AZURE_SEARCH_INDEX <customer-shortname>-knowledge
azd env set COSMOS_DATABASE <customer-shortname>

# Provision
azd provision

# Deploy
azd deploy
```

---

## Part 4 — Agent Customisation Guide {#part-4}

### Renaming the scenario

Replace all references to "Zava" with the customer brand:

=== "Python"

    ```bash
    # Find all Zava references in the Python track
    grep -r "Zava" src/python/app/agents/ --include="*.py" -l
    # Replace
    find src/python/app/agents/ -name "*.py" -exec sed -i 's/Zava/[CustomerName]/g' {} \;
    ```

=== ".NET"

    ```bash
    grep -r "Zava" src/dotnet/Agents/ --include="*.cs" -l
    Get-ChildItem src/dotnet/Agents/ -Recurse -Filter "*.cs" |
      ForEach-Object { (Get-Content $_) -replace 'Zava','[CustomerName]' | Set-Content $_ }
    ```

### Adding a new agent

1. Create the agent file:

    === "Python"

        ```bash
        cp src/python/app/agents/concierge.py src/python/app/agents/new_agent.py
        # Edit system prompt, tools, and registration
        ```

    === ".NET"

        ```bash
        cp src/dotnet/Agents/ConciergeAgent.cs src/dotnet/Agents/NewAgent.cs
        # Edit system prompt, tools, and DI registration
        ```

2. Register the agent in the orchestrator routing table.

3. Add the agent to the `/agents` endpoint response.

4. Write tests: `pytest tests/test_new_agent.py` / `dotnet test --filter Category=NewAgent`.

### Updating the knowledge base

1. Replace files in `data/policies/` with the customer's documents.
2. Re-run the seed script:

    ```bash
    # Python
    python scripts/seed_knowledge.py
    # .NET
    dotnet run --project ZavaApi -- --seed-knowledge
    ```

3. Verify citations point to the new source files.

---

## Part 5 — Handover Checklist {#part-5}

Complete this checklist at go-live.

### Technical handover

- [ ] Customer team can run `azd deploy` independently
- [ ] Runbook document shared with customer
- [ ] Application Insights dashboard set up and shared
- [ ] Alerting contact configured (customer email/Teams channel)
- [ ] Key Vault access policy includes customer's IT admin group

### Knowledge transfer

- [ ] Architecture walkthrough session completed (≥ 1 hour)
- [ ] Agent customisation training completed
- [ ] Disaster recovery procedure documented and tested
- [ ] Support escalation path agreed

### Commercial

- [ ] PAL/DPOR association established on customer subscription
- [ ] ACR tracking configured in Partner Center
- [ ] MSA/SOW signed and filed

---

## Part 6 — Evidence Collection Checklist {#part-6}

Collect Module B evidence **during** the customer delivery (do not wait until audit time):

| Milestone | Evidence to collect | Control |
|-----------|-------------------|---------|
| Infrastructure provisioned | `az resource list` output | B.2.1 |
| First `/chat` working | Agent transcript + `traceId` | B.1.1 |
| RAG working | Citations screenshot | B.1.1 |
| App Insights live | Trace waterfall screenshot | B.4.1 |
| Data agents working | Business unit query output | B.2.2 |
| Safety gate deployed | Blocked message screenshot | B.4.1 |
| `generate_evidence` run | `evidence/index.md` + case study | B.4.1 |
| PAL established | Partner Center screenshot | B.2.2 |

---

> **You have completed all Module B evidence templates.**
> Return to the [Evidence Index](b41-evidence-index.md) to verify coverage and export the bundle.
