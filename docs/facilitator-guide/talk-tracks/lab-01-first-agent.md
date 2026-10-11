# Talk Track — Lab 1: Your First Zava Agent

**Block:** Agentic Foundations (09:30–09:50) + Lab 1 (09:50–10:40)
**Slides:** Section 4 of `slides/zava-microhack-deck.md`
**Lab guide:** `docs/labs/lab-01-first-agent.md`
**Duration:** 20 min lecture + 50 min lab

---

## Agentic Foundations Lecture (09:30–09:50, 20 min)

### What is an AI agent? (5 min)

Start by drawing the agent loop on the whiteboard or using the slide diagram:

```text
Perception → Reasoning (LLM) → Tool call → Observation → repeat → Final response
```

Key points to land:

1. An agent is not a chatbot. It *decides* what to do, not just what to say.
2. **Tools** are the agent's hands — typed functions the LLM can choose to call.
3. **The LLM doesn't execute the tools** — it emits a structured tool-call intent; the framework executes it and returns the result.
4. **We don't hardcode routing logic.** The system prompt + tool descriptions tell the model when to use each tool. The model decides.

> Analogy: "An agent is like a new employee with access to a set of systems. You give them a job description (system prompt) and access to tools (Cosmos DB, AI Search). They figure out how to answer each question."

### Microsoft Agent Framework (5 min)

Two SDKs, identical patterns:

| | Python | .NET |
|---|---|---|
| Package | `agent-framework` | `Microsoft.Agents.AI` |
| Host | FastAPI | ASP.NET Minimal API |
| Tools | `@tool` decorator | `[AgentTool]` attribute |
| Inference | `InferenceProvider` | Same abstraction |

Key concepts to cover:

- **`Agent`** — has a system prompt, tool set, and inference provider
- **`Tool`** — typed function registered on the agent
- **`Workflow`** — deterministic multi-step process (not LLM-driven); used by Orchestrator for routing
- **`Handoff`** — Orchestrator transfers control + context to a specialist agent

### Python code walkthrough (5 min)

Show the `ConciergeAgent` sketch from the slides:

```python
from agent_framework import Agent, tool

class ConciergeAgent(Agent):
    system_prompt = "You are Zava's customer support agent..."

    @tool
    async def get_order(self, order_id: str) -> dict:
        """Retrieve order status from Cosmos DB."""
        return await self.cosmos.get_order(order_id)
```

Walk through:

1. `ConciergeAgent` extends `Agent` — inherits inference, message history, tool dispatch
2. `@tool` registers the function — the LLM can now call it
3. The docstring matters — it's included in the tool description the LLM sees
4. The return type matters — it's serialised back to the LLM as an observation

### Modular inference recap (2 min)

Quickly recap the three providers:

```bash
# Default (free, no Azure)
INFERENCE_PROVIDER=github
GITHUB_TOKEN=<PAT>

# Later (Azure)
INFERENCE_PROVIDER=foundry
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=...
```

"The agent code doesn't change. The factory wires the right client."

### Introduce Lab 1 (3 min)

Show the Lab 1 intro slide. Walk through what they'll build:

- Implement `ConciergeAgent` with `get_order`, `search_knowledge`, `create_return`
- Wire it into the `/chat` endpoint
- Test with order queries
- Verify `traceId` in the response

> "This is the first piece of B.1.1 evidence — a working AI agent on Azure (well, GitHub Models for now)."

---

## Lab 1 (09:50–10:40, 50 min)

### Expected lab flow

1. Attendees open `docs/labs/lab-01-first-agent.md`
2. They implement `ConciergeAgent` in their chosen track (`src/python/agents/concierge.py` or `src/dotnet/Agents/ConciergeAgent.cs`)
3. They run the API and test with the provided `curl` commands
4. Faster attendees explore the Orchestrator routing logic

### Circulate and watch for

- **Missing `GITHUB_TOKEN`** — most common issue; check `echo $GITHUB_TOKEN` in terminal
- **Tool not registered** — remind them the `@tool` decorator (or `[AgentTool]` attribute) must be present
- **Wrong model response** — check that `INFERENCE_PROVIDER=github` is set (default should be fine)
- **Port conflict** — if `8000` is in use, check for a previous run with `lsof -i :8000`

### Expected outcome by 10:40

Attendees can run:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the status of order ORD-001?"}'
```

And receive a response with:

```json
{
  "reply": "Order ORD-001 is currently shipped...",
  "agent": "concierge",
  "citations": [],
  "traceId": "4bf5122f..."
}
```

### Evidence checkpoint (2 min before break)

> "Before we break — note your evidence checkpoint. You've just built the first piece of
> B.1.1 evidence: a working AI agent on a production-pattern framework. Screenshot the
> response — that's your 'capability statement' artifact."

### Fallback for stragglers

Point stuck attendees to `docs/solutions/lab-01/` — they can copy the solution and keep up.

---

## Common questions during Lab 1

**Q: What exactly goes in the system prompt?**

> "The system prompt defines the agent's persona, its scope, and its decision-making rules.
> For Concierge: 'You are Zava's customer support agent. Use `get_order` for order queries
> and `search_knowledge` for policy and product questions.' Keep it concise and specific —
> verbose prompts tend to confuse the model."

**Q: How does the Orchestrator know to route to Concierge?**

> "The Orchestrator has its own system prompt that describes each specialist agent and when to
> use them. It calls the framework's handoff mechanism. You'll see the routing logic in
> `src/python/agents/orchestrator.py` — it's a workflow, not a neural decision."

**Q: What is `traceId`?**

> "It's the OpenTelemetry trace ID for this request. Right now it's generated locally. After
> Lab 3 (Deploy to Azure), it links to a real trace in Application Insights — you can click
> on it and see every agent step, tool call, and token count."

**Q: Can I add my own tool?**

> "Yes, and that's exactly what Lab 6 asks you to do. For now, implement the three tools in
> the lab guide. Experiment after the lab if you finish early."
