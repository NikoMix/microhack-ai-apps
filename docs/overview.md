# Overview — The Zava story

## Who is Zava?

**Zava** is Microsoft's 2025 fictional demo company (the successor to *Contoso* and *Fabrikam*). For
this microhack, Zava is an **intelligent athletic apparel** retailer: it sells smart garments
(connected running shirts, recovery leggings, temperature-adaptive jackets) across three business
units:

| Business unit | What it is | Used for |
|---|---|---|
| **Zava Retail Stores** | Physical stores + associates | Customer-diversity example (B.2.2) |
| **Zava eCommerce** | Web & mobile storefront | Customer-diversity example (B.2.2) |
| **Zava Wholesale** | B2B sales to gyms & teams | Customer-diversity example (B.2.2) |

## The business problem

Zava's customers, store associates, merchandisers, and operations staff all need fast, grounded,
trustworthy answers — about orders, products, inventory, suppliers, and policies. Zava's platform
team is building an **AI Agent Platform** on Azure to serve all of them through one governed entry
point.

## The solution you build

A multi-agent system on the **Microsoft Agent Framework**:

| Agent | Helps… | with… |
|---|---|---|
| **Concierge** | customers & associates | order status, returns, product Q&A (RAG-grounded) |
| **Merchandiser** | merchandising team | product insights, recommendations, review analysis |
| **Operations** | ops & supply chain | inventory, restock suggestions, supplier-doc parsing |
| **Trust & Compliance** | the whole org | content safety, governance, **audit-evidence generation** |
| **Orchestrator** | everyone | routes each request to the right specialist agent |

## Why it satisfies the Advanced Specialization

The *AI Applications on Microsoft Azure* Advanced Specialization (Module B) asks a partner to prove
**real AI delivery on Azure**, across **three revenue pillars** (AI, App Platform, Data), with
**certified people**, and an **organised audit package**. This microhack deliberately:

- builds a real AI solution on Azure (**B.1.1**),
- consumes services across **all three ACR pillars** (**B.2.1**),
- frames three Zava business units as diverse customers (**B.2.2**),
- maps each lab to the required certifications (**B.3.1**),
- and generates an **evidence package** (**B.4.1**) plus **onboarding assets** (**B.4.2**).

See the [Module B mapping](module-b-mapping.md) for the full crosswalk.

## Inference, your way

Every model call is **modular**. Set `INFERENCE_PROVIDER` to:

- `github` → **GitHub Models** (free; the default for Labs 0–2),
- `azure-openai` → **Azure OpenAI**,
- `foundry` → **Azure AI Foundry** (the recommended Azure path).

No image generation is used, so all three providers are fully interchangeable.
