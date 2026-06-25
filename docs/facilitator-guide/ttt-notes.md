# Train-the-Trainer (TTT) Notes

This guide is for **trainers re-delivering this microhack**. It covers qualification,
preparation, delivery, and customisation — everything you need to take what you learned
today and teach it to your own team or customer.

---

## What "qualified to deliver" means

After attending this TTT session, you are qualified to deliver the Zava AI MicroHack if you:

- [ ] Have completed Labs 0–3 yourself end-to-end (not just observed)
- [ ] Understand the **modular inference pattern** and can explain it without the slides
- [ ] Can describe the **Microsoft Agent Framework** tool-call lifecycle from memory
- [ ] Have read and understood the [Facilitator Guide](index.md) fully
- [ ] Have reviewed the [Pitfalls & Fixes](pitfalls.md) page
- [ ] Can answer the common questions listed in each talk-track without looking them up

You do **not** need to be an expert in all Azure services — the labs are designed so learners
can complete them with the guidance in `docs/labs/`. Your job is to frame the context,
demonstrate the patterns, and unblock stuck attendees.

---

## Before your first delivery

### Step 1 — Run the labs yourself (60–90 min)

Run Labs 0–2 in a fresh dev container before your delivery:

```bash
git clone https://github.com/NikoMix/microhack-ai-apps.git
cd microhack-ai-apps
# Open in dev container
export GITHUB_TOKEN=<your PAT>
cd src/python && make run
# Follow labs/lab-00, labs/lab-01, labs/lab-02
```

If you have an Azure subscription, also run Lab 3 (`azd up`). Time yourself — you'll need
this to manage the room's pace.

### Step 2 — Prepare your demo environment

1. Fork or clone the repo to your own GitHub account
2. Pre-pull the dev container image (`docker pull` before the day)
3. Export `GITHUB_TOKEN` in your terminal profile so it's always available
4. Optional: run `azd provision --preview` to confirm the Bicep templates validate

### Step 3 — Customise (optional)

You can customise the Zava story to fit your customer's industry. Replace "athletic apparel"
with your customer's domain, and update `data/products.json`, `data/policies/`, and the
agent system prompts. The build contract in `.microhack/build-contract.md` defines the
contract — don't change paths, agent keys, or the HTTP API without updating it.

---

## Delivery format options

### Option A — Full day (recommended)

Follow the [Run of Show](run-of-show.md) exactly. All 7 labs, all sections. Best for:

- Partner engineering teams learning to build and deliver this for customers
- Internal enablement where all attendees have a full day available

### Option B — Half day (Labs 0–3 only)

Cover: Welcome → Why AI Apps on Azure → Lab 0 → Agentic Foundations → Lab 1 → Grounding → Lab 2 → Azure Platform → Lab 3.

Demo Labs 4–6 instead of running them. This is the minimum viable path that covers:

- B.1.1 (working AI agent on Azure)
- B.2.1 (AI + App Platform pillars)
- Basic B.4.1 (tracing)

Use the [Run of Show](run-of-show.md) time-recovery options to compress.

### Option C — Deep dive (single topic)

Pick one section for a 90-minute deep dive:

| Topic | Sections | Slides |
|---|---|---|
| Agentic foundations | Agent Framework + Lab 1 | Section 4 |
| Modular inference | Inference + Lab 2 | Sections 3 + 5 |
| Azure deployment | Azure Platform + Lab 3 | Section 6 |
| Trust & governance | Trust + Lab 5 | Section 8 |
| GitHub Copilot + MCP | Build with AI + Lab 6 | Section 9 |

---

## Adapting for your audience

### Audience: technical executives / decision-makers (no coding)

- Remove the coding slides and labs
- Focus on: Why AI Apps on Azure, architecture, Module B mapping, evidence package demo
- Use the `trust.generate_evidence` demo as the centrepiece — show the output, not the code
- Time: ~2 hours

### Audience: junior developers

- Slow down the agent loop explanation — spend 10 minutes on it instead of 5
- Have attendees pair up (one Python, one .NET) to reduce track-switching
- Spend extra time on Lab 1 — it's the foundation everything else builds on
- Consider pre-running `azd up` from your account so they don't wait for Lab 3

### Audience: existing Azure architects

- Move quickly through the Azure Platform section — they know Container Apps and Bicep
- Spend more time on the modular inference pattern and the Agent Framework specifics
- Focus on the security model: Managed Identity, no keys, `DefaultAzureCredential`
- They'll appreciate the Module B mapping as a new commercial angle on familiar technology

### Audience: partners without Azure credits

- Run entirely on GitHub Models for Labs 0–3
- Demo Labs 3–6 from your own Azure subscription
- Emphasise: "The modular inference design means your code is identical whether running free or on Azure"
- Cost to demo from your account: < $5 for a 2-hour Azure demo

---

## What good facilitation looks like

### During lectures

- **Connect every slide to the evidence.** End every lecture section with: "This work satisfies [B.X.X] — here's the artifact it produces."
- **Draw, don't just click.** The agent loop diagram is more memorable when drawn on a whiteboard in real time.
- **Ask questions.** "If a user asks about a return, which tool should the model call?" — wait for an answer before moving on.

### During labs

- **Circulate constantly.** Don't sit at the front during labs. Walk the room every 5 minutes.
- **Don't fix; guide.** When an attendee is stuck, ask "what does the error say?" and "where is the data coming from?" before giving the answer.
- **Set a clear time box.** "You have 20 minutes. I'll announce when 10 minutes are left."
- **Point to solutions, not answers.** "The solution is in `docs/solutions/lab-01/` — look at the `ConciergeAgent` implementation if you're stuck."

### Managing pace

- If 20% of the room is stuck and 80% is moving, have the 80% review their neighbour's code while you help the stuck group.
- If everyone is stuck on the same thing, pause the lab, fix it on the projector, and resume.
- If you're running 30+ minutes behind by lunch, decide at lunch whether to demo Labs 4–6. Don't decide mid-afternoon — you'll lose momentum.

---

## Re-delivery checklist

### 1 week before

- [ ] Confirm venue / virtual meeting setup
- [ ] Send pre-requisites list to attendees (see [Prerequisites](prerequisites.md))
- [ ] Confirm attendee counts — order lunch/snacks accordingly
- [ ] Run Labs 0–3 yourself end-to-end on a clean machine

### 3 days before

- [ ] Pull the latest repo changes (`git pull`)
- [ ] Verify the dev container still builds cleanly
- [ ] Run `azd provision --preview` if you're doing an Azure demo
- [ ] Check for any breaking changes in `GITHUB_MODELS_CHAT_MODEL` or package versions

### Day before

- [ ] Pre-pull the dev container: `docker pull` from the devcontainer image
- [ ] Confirm the projector/AV setup ([A/V & Room Checklist](av-room-checklist.md))
- [ ] Print or download offline copies of: this guide, the pitfalls doc, the lab guides

### Day of

- [ ] Arrive 30 minutes early
- [ ] Run the pre-session sanity checks from the [A/V checklist](av-room-checklist.md)
- [ ] Open slides in browser (built HTML) or Marp VS Code extension
- [ ] Keep the [Pitfalls & Fixes](pitfalls.md) page open on your secondary screen

---

## After delivery

- [ ] Collect feedback using the GitHub Issue template (`.github/ISSUE_TEMPLATE/lab-feedback.yml`)
- [ ] File any bugs or improvements as issues on `NikoMix/microhack-ai-apps`
- [ ] Note any content that confused attendees or questions you couldn't answer — file an issue
- [ ] Update your attendees on any evidence they produced — remind them it's a starter pack for their real Advanced Specialization audit
- [ ] Share the repo link and the facilitator guide link with attendees for self-study

---

## Frequently asked TTT questions

**Q: How often is the repo updated?**

The repo follows the build contract in `.microhack/build-contract.md`. Check the main branch for
updates before each delivery. Subscribe to the repo's releases for notifications.

**Q: Can I brand this for my own company?**

Yes — the MIT licence permits this. Replace the Zava branding, update the scenario company,
and adapt the data files. Keep the build contract structure and the lab sequence — these
are designed to deliver the Module B evidence end-to-end.

**Q: What if I don't cover all the labs?**

The minimum viable path is Labs 0–3. These cover B.1.1 and B.2.1 (the technical and
App Platform evidence). Labs 4–6 add Data (B.2.1 Data pillar), Trust/Safety (B.4.1),
and the full evidence package (all controls). Decide based on your audience's time and goals.

**Q: Can I deliver this as a 2-day course?**

Yes — split at lunch on day 1 (after Lab 2) and start day 2 with the Azure Platform lecture.
This gives more time for each lab and deeper Q&A. The facilitator guide content works for
both formats.
