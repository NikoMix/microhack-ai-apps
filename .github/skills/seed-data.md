---
name: seed-data
description: >
  Seeds Zava data from data/ into Azure Cosmos DB (products, orders, customers)
  and PostgreSQL pgvector (chunked knowledge embeddings from policies/ and suppliers/).
  Requires COSMOS_ENDPOINT and POSTGRES_HOST to be set (azd output env vars).
---

# Skill: seed-data

Seeds the `data/` directory files into the Azure backends configured by `azd`.
Run this after `azd up` to populate Cosmos DB and PostgreSQL with the Zava
catalog, orders, customer records, and knowledge embeddings.

## Prerequisites

- `azd up` has completed successfully (all Azure resources provisioned)
- Environment variables emitted by azd are loaded (`.azure/<env>/.env` or shell)
- A Python venv is activated with `src/python` dependencies installed, **or**
  the .NET project has been restored

## Python track

```bash
# Activate venv (if not already)
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows

# Run the seed script
python src/python/scripts/seed.py \
  --cosmos-endpoint "$COSMOS_ENDPOINT" \
  --postgres-host   "$POSTGRES_HOST" \
  --data-dir        data/

# Or with all env vars loaded from azd:
azd env get-values | source  # bash — adjust for your shell
python src/python/scripts/seed.py
```

## .NET track

```bash
dotnet run --project src/dotnet/Zava.Seed -- \
  --data-dir data/
```

## What gets seeded

| Destination | Source file | Record count |
|-------------|-------------|:------------:|
| Cosmos DB `products` | `data/products.json` | 10 |
| Cosmos DB `orders` | `data/orders.json` | 6 |
| Cosmos DB `customers` | `data/customers.json` | 3 |
| PostgreSQL `knowledge` (pgvector) | `data/policies/*.md` + `data/suppliers/*.md` | 7 docs |

Embeddings use `text-embedding-3-small` (1536 dimensions) — provider selected
by `EMBEDDINGS_PROVIDER` env var (default: `github`).

## Verification

After seeding, verify with the Zava MCP server:

```bash
# Start MCP server (STDIO)
cd src/mcp-zava
npm start &

# Check inventory
echo '{"tool":"get_inventory"}' | node -e "..."
```

Or via the API:

```bash
curl http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"How many Pulse Smart Running Shirts are in stock?"}'
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| `COSMOS_ENDPOINT not set` | Run `azd env get-values` and export the vars |
| `Authentication failed` | Ensure `az login` with an identity that has Cosmos DB Data Contributor |
| `pgvector extension missing` | Run `CREATE EXTENSION vector;` in the `zava` PostgreSQL database |
| Embedding timeout | Set `EMBEDDINGS_PROVIDER=github` and ensure `GITHUB_TOKEN` is set |
