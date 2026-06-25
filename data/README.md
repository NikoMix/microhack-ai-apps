# Zava sample dataset

Synthetic, license-free seed data for the Zava AI Agent Platform. Used by **both** the Python and
.NET tracks for local/free mode (GitHub Models) and for seeding Azure Cosmos DB / PostgreSQL +
Azure AI Search in the Azure-native labs. No real personal data — names and figures are fictional.

## Files

| File | Shape | Used by | Goes to (Azure) |
|---|---|---|---|
| `products.json` | Smart-apparel catalog (10 items) | Merchandiser, Concierge | Cosmos DB `products` |
| `reviews.json` | Product reviews | Merchandiser | Cosmos DB `reviews` |
| `orders.json` | Orders across 3 business units | Concierge, Operations | Cosmos DB `orders` |
| `customers.json` | 3 Zava business units (B.2.2 diversity) | Operations, Trust | Cosmos DB `customers` |
| `policies/*.md` | Returns, warranty, sizing, care, sustainability | Concierge (RAG) | PostgreSQL pgvector + AI Search index `zava-knowledge` |
| `suppliers/*.md` | PO + invoice samples | Operations (Doc Intelligence) | Blob (Doc Intelligence input) |

## Embedding contract
- Knowledge docs are chunked and embedded with **1536-dim** vectors (`text-embedding-3-small`).
- pgvector column: `vector(1536)`; AI Search vector field dimension: **1536**.
- Keep this dimension consistent across providers (GitHub Models / Azure OpenAI / Foundry).

## Conventions
- IDs are stable (`ZAVA-*`, `ZO-*`, `SUP-*`) so labs and tests can reference them deterministically.
- Currency is USD. Dates are ISO `YYYY-MM-DD`.
- Add new items by following the existing schema; keep JSON valid (CI lints these).

> Loader scripts live with each track (`src/python/scripts/seed.py`, `src/dotnet/.../Seed`). They read
> these files so the two tracks stay behaviourally identical.
