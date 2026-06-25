# Solution 1 — Your First Zava Agent (Concierge)

> **Facilitator note:** The 50-minute slot includes exploration time. Students often spend
> 10–15 min reading the agent code. The most valuable checkpoint is seeing `traceId` in every
> response and observing the orchestrator triage correctly.

## Expected command outputs

### Agent listing (confirming concierge is registered)

```json
[
  { "key": "concierge", "name": "Zava Concierge", "description": "..." },
  ...
]
```

### Order status query (Step 3)

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the status of order ZO-001?", "agent": "concierge"}' \
  | python -m json.tool
```

```json
{
  "reply": "Order ZO-001 for Zava Retail Stores contains 2 items (ZP-001 × 2, ZP-003 × 1) and is currently in 'shipped' status. Expected delivery: 2025-07-05.",
  "agent": "concierge",
  "citations": [],
  "traceId": "7a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d"
}
```

### Multi-turn conversation (Step 4)

**Turn 1:**

```json
{
  "reply": "I can help you start a return for the ZP-001 Connected Running Shirt from order ZO-001. Returns are accepted within 90 days for unworn items. Would you like me to initiate the return process?",
  "agent": "concierge",
  "citations": [],
  "traceId": "1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d"
}
```

**Turn 2 (context preserved from Turn 1):**

```json
{
  "reply": "Zava's return policy allows returns within 90 days for unworn, unwashed items with original tags. For smart garments like the ZP-001, the embedded sensor module must be intact. You can return it by mail or at any Zava Retail Store. Since you mentioned returning your ZP-001 from ZO-001, I can initiate that now if you'd like.",
  "agent": "concierge",
  "citations": [],
  "traceId": "2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d5e"
}
```

_Facilitator note: the key point is that Turn 2 references the shirt from Turn 1 without re-stating the order. If a student's session does NOT show this continuity, check that they used the same `sessionId`._

### get_product tool (Step 5)

```json
{
  "reply": "The ZP-001 Connected Running Shirt is a smart garment with integrated biometric sensors. It monitors heart rate, cadence, and skin temperature in real-time. Available in sizes XS–XXL in Midnight Blue and Solar Orange. Price: $149.99. It is compatible with the Zava mobile app via Bluetooth 5.2.",
  "agent": "concierge",
  "citations": [],
  "traceId": "3c4d5e6f1a2b3c4d5e6f1a2b3c4d5e6f"
}
```

### Orchestrator triage (Step 6)

```json
{
  "reply": "I can see that order ZO-002 for Zava eCommerce is currently in 'processing' status — it hasn't shipped yet. Processing typically takes 1–2 business days. I have flagged it for our operations team to prioritise. Is there anything else I can help you with?",
  "agent": "concierge",
  "citations": [],
  "traceId": "4d5e6f1a2b3c4d5e6f1a2b3c4d5e6f1a"
}
```

_Note: `"agent": "concierge"` — the orchestrator triaged an order question to concierge._

## Filled evidence artifacts

### b11-agent-transcript-lab1.txt

```text
[SESSION: lab1-demo | 2025-07-01T09:55:00Z]

Turn 1
User: I want to return the connected running shirt from order ZO-001.
Agent (concierge): I can help you start a return for the ZP-001 Connected Running Shirt from
order ZO-001. Returns are accepted within 90 days for unworn items. Would you like me to
initiate the return process?
traceId: 1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d

Turn 2
User: What is your return policy?
Agent (concierge): Zava's return policy allows returns within 90 days for unworn, unwashed
items with original tags. For smart garments like the ZP-001, the embedded sensor module must
be intact. You can return it by mail or at any Zava Retail Store. Since you mentioned returning
your ZP-001 from ZO-001, I can initiate that now if you'd like.
traceId: 2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d5e
```

## Common failure modes

| Failure | Root cause | Fix |
|---------|-----------|-----|
| `"agent": "orchestrator"` (not concierge) | Orchestrator triage went wrong | Check system prompt in orchestrator; ensure concierge is registered |
| Empty reply | LLM returned no content | Check `GITHUB_TOKEN`; try a simpler prompt |
| `order not found` | Wrong order ID | IDs are `ZO-001`–`ZO-010`; check `data/orders.json` |
| `traceId` is null | OTel not initialised | Check startup logs for OTEL initialization errors |
