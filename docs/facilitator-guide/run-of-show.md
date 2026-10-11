# Run of Show — Full 1-Day Timing

Use this as your live timing reference. The table includes setup cues, demo marks, and fallback
options so you can adapt on the fly.

## Before the day

- [ ] Clone / update repo and confirm dev container builds
- [ ] Export your `GITHUB_TOKEN` and test with GitHub Models
- [ ] Run `azd provision --preview` to verify infrastructure (optional: `azd up` for your own instance)
- [ ] Open the slides deck: `slides/zava-microhack-deck.md`
- [ ] Print or bookmark this guide and the pitfalls doc

---

## Morning

### 08:15 — Trainer arrives / room setup

- Open dev container in VS Code on your laptop
- Test `curl http://localhost:8000/health` from a running API
- Display slide 1 (title) on the projector
- Have the GitHub Models `curl` example ready in a terminal tab

---

### 08:30 — Welcome & TTT Orientation (15 min)

**Slides:** Section 0 (Welcome, about this deck, agenda)

**Objectives:**

- Attendees understand what TTT means — they will re-deliver this
- Everyone has the repo cloned; dev container is downloading in the background
- Framing: "This is Module B evidence-in-a-day"

**Talk-track key points:**

1. Introduce yourself + your role delivering this specialization
2. Explain Train-the-Trainer: "You are the audience for a course you'll teach. Watch how I frame things, not just what I say."
3. Show the agenda slide — emphasise labs are the spine
4. Two tracks: ask for a show of hands Python vs .NET
5. Point out the Facilitator Guide — "This is your cheat sheet when you re-deliver"

**Demo cue:** None needed — keep energy high, move fast.

**Fallback:** If dev containers are slow to pull, acknowledge it and move on — attendees can complete Lab 0 during the lecture slot.

---

### 08:45 — Why AI Apps on Azure + Zava Story (25 min)

**Slides:** Sections 1–2 (Advanced Spec, Module B, pillars, Zava story, architecture)

**Objectives:**

- Attendees understand the business reason for building this
- The 3 ACR pillars are mapped to the services they'll use
- Zava = a real story they can repeat to a customer

**Talk-track key points:**

1. Frame the Advanced Specialization: "This is a Microsoft validation that you can deliver real AI on Azure, across all three pillars, with proven customers and certified staff. Module B is the technical requirements section."
2. Walk through the Module B controls table — point out that Labs 1–6 produce the evidence
3. Introduce Zava: "Microsoft's 2025 demo company — intelligent athletic apparel. We're the platform team building their AI agent platform. Every lab we do today adds a feature to this platform and produces an audit artifact."
4. Show the architecture diagram — trace a request: User → API → Orchestrator → Concierge → AI Search + Cosmos → Trust check → response
5. Emphasise modular inference: "Same agent code, three different AI backends — GitHub Models today (free), Azure tomorrow"

**Demo cue:** Show the architecture diagram slide. Point to the three pillars and name one service in each.

---

### 09:10 — Lab 0: Environment & GitHub Models (20 min)

**Lab guide:** [`talk-tracks/lab-00-welcome.md`](talk-tracks/lab-00-welcome.md)

**Objectives:**

- Every attendee has a working dev container
- GitHub PAT is set; first inference call succeeds
- Health and agents endpoints respond

**Recovery fallback:** If Docker/container issues, attendees can use GitHub Codespaces.

---

### 09:30 — Agentic Foundations (20 min)

**Slides:** Section 4 (agents, Agent Framework, Python + .NET sketches)

**Objectives:**

- Attendees understand the agent loop: perceive → reason → act (tool call) → observe → repeat
- Microsoft Agent Framework = tools + system prompt + inference provider
- The two tracks are symmetrical

**Talk-track key points:**

1. Draw the agent loop on whiteboard or walk through the slide diagram
2. Explain tools: "A tool is a typed Python/C# function. The LLM decides when to call it based on the system prompt and the user message. We never hardcode 'if question about orders, call get_order' — the model decides."
3. Explain handoff: "The orchestrator doesn't answer questions — it decides who should answer and passes the conversation to that agent."
4. Quick comparison of Python vs .NET: same concepts, different syntax

**Demo cue:** Show the Python `ConciergeAgent` code sketch — point to the `@tool` decorator and the `search_knowledge` method. Ask: "What happens when a user asks 'Can I return these leggings?' — which tool does the model call?"

---

### 09:50 — Lab 1: Your First Zava Agent (50 min)

**Lab guide:** [`talk-tracks/lab-01-first-agent.md`](talk-tracks/lab-01-first-agent.md)

**This is the first substantial lab.** Give attendees time. Circulate and help.

---

### 10:40 — Break (15 min)

Use this time to:

- Reset the slides to Section 5 (Grounding & RAG)
- Check Lab 1 stragglers and point them to the solution branch
- Test the RAG demo on your machine

---

### 10:55 — Grounding & RAG (15 min)

**Slides:** Section 5 (embeddings, AI Search, pgvector, citations)

**Talk-track key points:**

1. "Without grounding, the agent makes up policies and prices. RAG fixes this."
2. Walk through the pipeline: query → embed → vector search → top-k chunks → augmented prompt → grounded reply
3. Explain the citations array: "Every response tells the user where the information came from. This is also an audit trail for the safety review."
4. Quick mention of pgvector as an alternative for teams already on PostgreSQL

**Demo cue:** Show a `curl` call returning a response with `citations[]` populated.

---

### 11:10 — Lab 2: Ground It (50 min)

**Lab guide:** [`talk-tracks/lab-02-rag.md`](talk-tracks/lab-02-rag.md)

**Key demo:** Live provider swap from GitHub Models to `foundry` or `azure-openai`.

---

### 12:00 — Lunch (45 min)

---

## Afternoon

### 12:45 — Azure Platform (20 min)

**Slides:** Section 6 (azd, Bicep/AVM, Container Apps, Managed Identity)

**Talk-track key points:**

1. "`azd up` = one command to provision + build + deploy the entire platform"
2. Walk through what gets provisioned: Container Apps, ACR, AI Foundry, AI Search, Cosmos, Postgres, Key Vault, App Insights
3. Emphasise Managed Identity: "No connection strings. No API keys. `DefaultAzureCredential` figures it out — in dev it uses your `az login`; in production it uses the user-assigned Managed Identity we provision."
4. Bicep/AVM: "These are the IaC templates. We're using Azure Verified Modules — Microsoft-maintained, opinionated, secure-by-default blueprints."

**Demo cue:** Show `azd provision --preview` output listing the resources to be created.

---

### 13:05 — Lab 3: Deploy to Azure (55 min)

**Lab guide:** [`talk-tracks/lab-03-deploy.md`](talk-tracks/lab-03-deploy.md)

**Requires:** Azure subscription. If attendees don't have one, demo from your account.

---

### 14:00 — Data Agents (15 min)

**Slides:** Section 7 (Cosmos DB, PostgreSQL + pgvector, data-grounded tools)

**Talk-track key points:**

1. Show the Cosmos DB schema: three containers, their key fields, which agent owns each
2. Explain `disableLocalAuth: true` — "We disabled Cosmos DB keys entirely. The app must use Managed Identity. This is a Module B B.4.1 security requirement."
3. pgvector: "Same PostgreSQL you already have, with a vector extension. Great for teams that don't want another managed service for embeddings."

---

### 14:15 — Lab 4: Data Agents (45 min)

**Lab guide:** [`talk-tracks/lab-04-data-agents.md`](talk-tracks/lab-04-data-agents.md)

---

### 15:00 — Break (15 min)

---

### 15:15 — Trust, Safety & Governance (15 min)

**Slides:** Section 8 (Content Safety, OpenTelemetry, OWASP for agents)

**Talk-track key points:**

1. "Every draft reply passes through a safety gate before it reaches the user."
2. Show the safety gate diagram: agent reply → `content_safety_check()` → Content Safety API → safe/blocked
3. OpenTelemetry: "`traceId` in every response links user-visible output to a full trace in App Insights — tool calls, latency, token usage, agent handoffs."
4. OWASP top risks table — connect each to a concrete control in the platform

---

### 15:30 — Lab 5: Trust & Observability (45 min)

**Lab guide:** [`talk-tracks/lab-05-trust.md`](talk-tracks/lab-05-trust.md)

---

### 16:15 — Build with AI — GitHub Agents, Skills & MCP (15 min)

**Slides:** Section 9 (custom agents, skills, MCP)

**Talk-track key points:**

1. "You've built AI agents. Now let's build with AI — using Copilot to extend the platform."
2. Custom agents in `.github/agents/` — they're YAML files, accessible in Copilot Chat
3. Skills in `.github/skills/` — extend agents with callable actions
4. MCP servers — "Any data source, any tool, accessible to any AI model that speaks MCP"
5. The Zava MCP server: `src/mcp-zava/` provides catalog, orders, and policies to Copilot

---

### 16:30 — Lab 6: Capstone (45 min)

**Lab guide:** [`talk-tracks/lab-06-capstone.md`](talk-tracks/lab-06-capstone.md)

---

### 17:15 — Evidence Review & Audit Readiness (15 min)

**Slides:** Section 10 (evidence-as-you-go, customer diversity, cert crosswalk)

**Talk-track key points:**

1. Walk through the generated evidence package structure
2. Customer diversity table: "Here's how to document your 3+ customers for B.2.2"
3. Cert crosswalk: "Here's the study plan — which labs map to which exam objectives"
4. Emphasise: "You leave today with a starter evidence pack. Adapt it for a real engagement."

---

### 17:30 — TTT Debrief & Close (15 min)

**Slides:** Section 11 (TTT checklist, delivery tips, thank you)

**Talk-track key points:**

1. Re-delivery checklist: "Before you deliver, run Labs 0–2 yourself end-to-end."
2. Top 3 delivery tips: show live code, connect every slide to the evidence, let them struggle briefly
3. Point to Facilitator Guide and pitfalls doc as their reference material
4. Q&A and wrap

---

## Time recovery options

| Situation | Recovery action |
|---|---|
| Lab 0 takes too long | Pair attendees on one machine; move to Lab 1 |
| Lab 1 takes > 60 min | Use solution branch; continue with the working agent |
| No Azure subscription | Demo Labs 3–4 from trainer's account; attendees observe |
| Lab 3 fails (`azd up`) | Pre-provision your own Azure instance; share the endpoint |
| Lab 5 hangs (Content Safety) | Use mock safety gate (returns `safe: true`); explain the real API |
| Running 30 min behind | Demo Labs 5 and/or 6 instead of having attendees run them |
