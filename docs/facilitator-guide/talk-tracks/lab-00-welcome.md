# Talk Track — Welcome, Zava Story & Why AI Apps on Azure

**Blocks:** Welcome & TTT (08:30–08:45) + Why AI Apps on Azure (08:45–09:10)
**Slides:** Sections 0–2 of `slides/zava-microhack-deck.md`
**Duration:** ~40 minutes total

---

## 08:30 Welcome & TTT Orientation (15 min)

### Opening (2 min)

Welcome everyone. Introduce yourself briefly — name, role, how you use Azure AI in your work.

> "Today is a little different from a typical workshop. You are not just the audience — you are
> the future trainers. Pay attention to *how* I frame things, not just *what* I say."

### What TTT means (3 min)

- A **Train-the-Trainer** session means attendees leave qualified to re-deliver this course
- The Facilitator Guide (this document) is their cheat sheet
- Encourage them to ask: "Why did you do it that way?" as well as technical questions

### Agenda overview (5 min)

Walk through the agenda slide:

- Emphasise that **labs are the majority of the day** (~3h 45min)
- Point out the evidence checkpoints at the end of each lab
- "If we run short on time, I'll demo Labs 5–6. You'll still see the outcome."

### Two tracks — confirm choice (3 min)

Show of hands: Python vs .NET. Confirm the lab guide they should follow.
Both tracks behave identically — "same agents, same API, same labs."

### Housekeeping (2 min)

- Breaks: 10:40 and 15:00
- Lunch: 12:00
- Dev containers should be pulling — that's fine, we'll get to Lab 0 in 15 minutes
- Share the repo URL and the Facilitator Guide location

---

## 08:45 Why AI Apps on Azure (25 min)

### The Advanced Specialization (7 min)

Advance to the "Advanced Specialization" slide.

> "The *AI Applications on Microsoft Azure* Advanced Specialization is Microsoft's partner
> validation for delivering real AI solutions on Azure. It's a commercial and technical
> designation — it shows enterprise customers that you've done this before."

Walk through the 5 requirements:

1. **Technical capability** — B.1.1: a real AI solution on Azure (we build this today)
2. **Revenue across 3 pillars** — B.2.1: AI, App Platform, and Data (our architecture hits all 3)
3. **Customer diversity** — B.2.2: three unique customers (we model Zava's 3 business units)
4. **Certified staff** — B.3.1: AZ-204, AI-102, DP-420, AZ-400 (we map labs to exams)
5. **Organised evidence** — B.4.1/B.4.2: an indexed package (the `trust` agent assembles it)

> "Most partners know they need the specialization but don't know how to build the evidence.
> By the end of today you'll have a starter evidence pack you can adapt for a real audit."

### Module B controls table (5 min)

Walk through the controls table slide. Point out that the columns map to labs.

> "Notice that almost every lab touches B.1.1 — because every lab adds to the real AI solution
> we're building. The evidence isn't separate from the work; it *is* the work."

### The 3 ACR pillars (3 min)

Show the pillars box diagram. Name one service per pillar:

- AI Services: Azure AI Foundry (+ OpenAI, AI Search, Content Safety)
- App Platform: Azure Container Apps (+ ACR, API Management, GitHub)
- Data: Cosmos DB (+ PostgreSQL with pgvector)

> "Our architecture deliberately touches all three. That's how you build ACR across the pillars."

### The Zava story (5 min)

Advance to the Zava slide.

> "Zava is Microsoft's 2025 fictional demo company — the successor to Contoso and Fabrikam.
> Think Lululemon with IoT sensors in the fabric. Smart running shirts that track heart rate,
> recovery leggings that adjust compression, jackets that adapt to temperature."

Introduce the three business units:

- **Retail Stores** — physical stores, store associates asking 'where is order X?'
- **eCommerce** — web + mobile, customers asking about returns and product specs
- **Wholesale** — B2B to gyms and sports teams, needing bulk inventory and supplier docs

> "For Module B's customer diversity requirement, these three units play the role of three
> distinct customers. We'll come back to how you document that in the evidence package."

### The Zava platform (5 min)

Advance to the architecture slide.

Walk through the request flow:

1. User asks: "Can I return these leggings?"
2. Request hits API Management → Container Apps (`api-python` or `api-dotnet`)
3. Orchestrator receives the message → decides it's a support question → hands off to Concierge
4. Concierge calls `search_knowledge("returns policy")` → AI Search returns policy chunks
5. Concierge calls `content_safety_check(draft reply)` via Trust agent → safe
6. Response returned: `{ reply, citations, traceId }`

> "This is the architecture you'll build today. It's also the B.1.1 architecture-diagram
> evidence artifact — you'll export it from the docs at the end of Lab 6."

---

## Demo cues

### Demo 1 — End-to-end API call (run during architecture walkthrough)

```bash
# Show the running API responding to a query
curl -s http://localhost:8000/health | python -m json.tool
curl -s http://localhost:8000/agents | python -m json.tool
```

If Lab 0 isn't done yet, show the output from your pre-prepared terminal.

---

## Common questions at this stage

**Q: What's the difference between this microhack and an AZ-204 training course?**

> "AZ-204 is about individual developer skills. This microhack is about building a *complete
> platform* that satisfies a *partner-level* commercial specialization. The cert crosswalk shows
> how today's labs *contribute* to those exams — but the focus is the specialization, not the cert."

**Q: Can I use this with a customer?**

> "Yes — that's exactly the point. The Zava story is fictional, but the architecture, the agent
> patterns, and the evidence package are real. Replace Zava with your customer's name and you
> have a reference architecture and an evidence template."

**Q: Do I need to do all 7 labs to get the Advanced Specialization?**

> "The specialization requires real *customer* engagements — not classroom labs. This microhack
> teaches you *how* to build the capability and *how* to organise the evidence. The controls
> B.2.1/B.2.2/B.3.1 are organisational pre-qualifications you bring from your real business."
