# Facilitator Guide — Zava AI MicroHack

> **For trainers only.** This guide tells you *how to run* the microhack — timing, talk-tracks,
> demo cues, pitfalls, and how to re-deliver it yourself. Attendees don't need this.

## Quick navigation

| You need… | Go to |
|---|---|
| Full run-of-show with timing | [Run of Show](run-of-show.md) |
| Environment & prerequisites | [Prerequisites](prerequisites.md) |
| Per-lab talk track + demo cues | [Talk Tracks](talk-tracks/) |
| Common problems & fixes | [Pitfalls & Fixes](pitfalls.md) |
| Room + A/V setup checklist | [A/V & Room Checklist](av-room-checklist.md) |
| How to re-deliver this as TTT | [Train-the-Trainer Notes](ttt-notes.md) |

## Course overview

This is a **1-day, instructor-led, Train-the-Trainer microhack**. By the end, every attendee can:

1. Build a multi-agent AI application on **Microsoft Agent Framework** (Python or .NET)
2. Deploy it to Azure via `azd up` (Container Apps + AI Foundry + Cosmos DB + PostgreSQL)
3. Understand **modular inference** — GitHub Models, Azure OpenAI, Azure AI Foundry
4. Produce and organise an **Advanced Specialization Module B evidence package**
5. **Re-deliver** this course themselves

### Duration and pace

- **Total:** ~7.5 hours including breaks
- **Labs are the spine** (~3h 45min hands-on). Keep lectures tight — they are framing, not deep-dives.
- If short on time, Labs 0–3 are the minimum viable path; Labs 4–6 can be demoed by the trainer.
- If attendees have no Azure subscription, run entirely on **GitHub Models** and demo Labs 3–6.

### Two tracks

Attendees choose **Python** (`src/python/`, FastAPI + `agent-framework`) or **.NET**
(`src/dotnet/`, Minimal API + `Microsoft.Agents.AI`). Both implement the same agents,
the same HTTP API, and follow identical lab steps. You don't need to run both tracks —
pick the one you're most comfortable demonstrating.

## Lab sequence

```text
Lab 0  →  Lab 1  →  Lab 2  →  Lab 3  →  Lab 4  →  Lab 5  →  Lab 6
Setup    Concierge    RAG     Deploy   Data agents   Trust   Capstone
                  (GitHub ──→ Azure)
```

Each lab ends with an **evidence checkpoint** that names the artifact produced and the
Module B control it satisfies.

## Module B mapping summary

| Lab | B.1.1 | B.2.1 | B.2.2 | B.3.1 | B.4.1 | B.4.2 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | | | | ● | | |
| 1 | ● | | | ● | | |
| 2 | ● | ● | | ● | | |
| 3 | ● | ● | | ● | | ● |
| 4 | ● | ● | ● | ● | | |
| 5 | ● | | | ● | ● | |
| 6 | ● | ● | ● | ● | ● | ● |

Full control-to-artifact mapping: [`docs/module-b-mapping.md`](../module-b-mapping.md)

## Key resources

- **Agenda:** [`docs/agenda.md`](../agenda.md)
- **Architecture:** [`docs/architecture.md`](../architecture.md)
- **Build contract:** [`.microhack/build-contract.md`](../../.microhack/build-contract.md)
- **Slides:** [`slides/zava-microhack-deck.md`](../../slides/zava-microhack-deck.md)
- **Labs:** `docs/labs/` (student-facing)
- **Solutions:** `docs/solutions/` (reference implementations)
- **Evidence templates:** `docs/evidence-templates/`
