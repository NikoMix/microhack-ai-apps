# Talk Track — Lab 6: Capstone (GitHub Agents, Skills & MCP + Evidence Pack)

**Block:** Build with AI lecture (16:15–16:30) + Lab 6 (16:30–17:15) + Evidence review (17:15–17:30)
**Slides:** Sections 9–10 of `slides/zava-microhack-deck.md`
**Lab guide:** `docs/labs/lab-06-capstone.md`
**Duration:** 15 min lecture + 45 min lab + 15 min evidence review

---

## Build with AI Lecture (16:15–16:30, 15 min)

### The shift: building AI → building with AI (2 min)

> "Labs 0–5: you built an AI platform. Now: how do you use AI to extend and maintain
> that platform? GitHub Copilot, custom agents, skills, and MCP servers turn your
> repository into an AI-assisted development environment."

### GitHub Copilot custom agents (5 min)

Custom agents live in `.github/agents/` and are accessible in Copilot Chat as `@AgentName`.

```yaml
# .github/agents/zava-architect.yml
name: ZavaArchitect
description: Expert on the Zava AI Agent Platform
model: gpt-4o
instructions: |
  You are the Zava platform architect. Help developers extend agents,
  review IaC changes, and map features to Module B controls.
tools:
  - type: code_search
  - type: file_search
```

> "This agent has full repo context — it reads your code, your IaC, your tests.
> Ask it 'Does this new agent follow the modular inference pattern?' and it checks
> your actual implementation against the build contract."

Key use cases for the ZavaArchitect agent:

- Code review for new agent implementations
- Answering "which Module B control does this feature satisfy?"
- Suggesting test cases based on existing test patterns
- Reviewing Bicep changes for security compliance

### Copilot skills (3 min)

Skills extend agents with **callable actions** registered in `.github/skills/`:

```yaml
# .github/skills/generate-evidence.yml
name: GenerateEvidence
description: Compile Module B evidence from lab outputs
parameters:
  - name: controls
    type: string[]
```

Usage in Copilot Chat:

> `@ZavaArchitect /generate-evidence controls:["B.1.1","B.4.1"]`

→ calls the skill → HTTP call to the running API → `trust.generate_evidence()` → returns evidence package

### MCP servers (5 min)

MCP (Model Context Protocol) makes any tool accessible to any MCP-compatible AI client:

```text
GitHub Copilot / Claude / GPT
         │
     MCP client
         │
     MCP server (src/mcp-zava/, port 3100)
         │
  ┌──────┼──────┐
  ▼      ▼      ▼
Products  Orders  Policies
```

The Zava MCP server (`src/mcp-zava/`) exposes:

- `get_product(id)` — product details from Cosmos DB
- `search_products(query)` — semantic search
- `get_order(id)` — order status
- `search_policies(query)` — policy search via AI Search

`mcp.json` at the repo root configures MCP for VS Code and GitHub Copilot:

```json
{
  "servers": {
    "zava": {
      "url": "http://localhost:3100/mcp",
      "description": "Zava catalog, orders, and policies"
    }
  }
}
```

> "Once MCP is configured, Copilot can answer 'What's the current stock of the
> Alpha running shirt?' by querying the Zava MCP server directly — no copy-pasting,
> no context switching."

---

## Lab 6 (16:30–17:15, 45 min)

### Expected lab flow

1. **Part A (20 min):** Create a new GitHub Copilot custom agent in `.github/agents/`
   - Extend the ZavaArchitect agent or create a new domain-specific agent
   - Register a skill that calls a Zava API tool
   - Test in Copilot Chat

2. **Part B (15 min):** Start the Zava MCP server and test
   ```bash
   cd src/mcp-zava && npm start
   # Then in Copilot Chat: ask about a Zava product
   ```

3. **Part C (10 min):** Generate the full evidence package
   ```bash
   curl -X POST http://localhost:8000/chat \
     -d '{"message": "Generate Module B evidence for all controls"}'
   ```
   Review the output structure and the evidence index.

### Demo cue — Copilot + MCP live

Show Copilot Chat with the Zava MCP server running:

1. Type: `What products does Zava sell in the running category?`
2. Copilot should invoke the MCP server's `search_products` tool
3. Show the response includes real products from the Zava catalog

> "This is AI-augmented development in practice. Your tools, your data, your agents —
> all accessible from within the development environment."

### Demo cue — evidence package

Show the generated evidence package structure:

```text
evidence/
├── index.md              ← B.1.1 → architecture-diagram.md, capability-statement.md
│                            B.2.1 → pillar-worksheet.md
│                            ...
├── B.1.1-architecture/
│   ├── architecture-diagram.md
│   └── capability-statement.md
├── B.4.1-audit/
│   └── evidence-index.md
└── ...
```

Walk through the index — show how each control maps to a concrete artifact.

> "This is what you hand to an auditor. Adapt the capability statement with your
> company name and real customer names. The structure and the framework are already there."

### Watch for

- **Copilot agent not appearing** — check that the YAML syntax is valid and the file is in `.github/agents/`. It may take a minute to reload in Copilot Chat.
- **MCP server port conflict** — default is `3100`. If in use, update `mcp.json` and the server config.
- **`generate_evidence` timeout** — the tool makes multiple API calls. If slow, check the Content Safety endpoint is healthy and the AI Search index is populated.
- **Missing evidence artifacts** — if earlier labs weren't completed, some evidence sections will be empty. That's OK — the structure is what matters; attendees will fill it in their real engagements.

---

## Evidence Review (17:15–17:30, 15 min)

### Walk through the evidence package (8 min)

Go back to the slides: Section 10 (Evidence Review).

Walk through each control and point to the artifact that satisfies it:

1. **B.1.1** — architecture diagram + capability statement + working code
2. **B.2.1** — pillar worksheet showing AI Search / Container Apps / Cosmos DB
3. **B.2.2** — customer diversity table (3 Zava business units)
4. **B.3.1** — cert crosswalk table
5. **B.4.1** — evidence index + safety gate log + App Insights trace
6. **B.4.2** — onboarding pack + delivery templates

> "In a real engagement, you replace 'Zava' with your customer's name and fill in
> the real revenue, association types, and certified staff. The template is already
> structured to match what Microsoft's audit process expects."

### Customer diversity B.2.2 (3 min)

Walk through the customer diversity table and the association types:

| Business unit | Association type |
|---|---|
| Zava Retail Stores | DPOR |
| Zava eCommerce | PAL |
| Zava Wholesale | CSP |

> "For your real audit: you need 3 unique customers, each associated via DPOR, PAL,
> or CSP in Partner Center. This template shows the columns the auditor expects."

### Cert crosswalk B.3.1 (2 min)

Point to `docs/cert-crosswalk.md`.

> "B.3.1 requires 5 certified individuals across AZ-204, AI-102, DP-420, and AZ-400.
> The lab crosswalk maps today's labs to those exam objectives — use it to justify
> time spent on this course in a study plan."

### Wrap (2 min)

> "You leave today with: a working multi-agent AI platform, a Module B evidence
> starter pack, and the skills to re-deliver this course. The next step is to take
> what you built today and apply it to a real customer engagement — and then submit
> your Advanced Specialization application."

---

## Common questions at end of day

**Q: How do I submit the Advanced Specialization application?**

> "Through Partner Center. You'll submit the evidence package, the customer associations,
> and the cert verification. Microsoft's partner team reviews it. The timeline is typically
> 4–6 weeks. This microhack gives you the technical foundation and the evidence template —
> you bring the real customers and the real certifications."

**Q: Can I use this platform as a production starting point?**

> "Absolutely. The platform is production-pattern: Managed Identity, no keys, IaC with AVM,
> OpenTelemetry, Content Safety, Container Apps. You'd need to add: a real frontend,
> customer-specific agents and knowledge, production capacity planning, and a formal
> security review. But the bones are production-ready."

**Q: What if I want to add a new agent after today?**

> "Create a new class extending `Agent`, register it in the Orchestrator's system prompt,
> add its tools, and deploy with `azd deploy`. The ZavaArchitect Copilot agent can help
> you check that you've followed all the patterns. The build contract in `.microhack/`
> is your reference."
