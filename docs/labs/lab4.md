# Lab 4 — Data Agents: Merchandiser & Operations

> **Estimated time:** 45 minutes
> **Module B controls:** B.1.1 (Azure AI Implementation), B.2.1 (ACR Performance — Data pillar),
> B.2.2 (Customer Diversity), B.3.1 (Certifications)

## Learning objectives

By the end of this lab you will be able to:

1. Invoke the `merchandiser` agent's tools (`search_products`, `get_reviews`, `sales_trends`).
2. Invoke the `operations` agent's tools (`get_inventory`, `restock_suggestion`).
3. Use the `operations` agent to parse a supplier document with **Azure Document Intelligence**.
4. Query Cosmos DB data across the three Zava business units (B.2.2 customer diversity).
5. Trace a Cosmos DB query to Application Insights.

## Prerequisites

- Lab 3 complete — infrastructure provisioned; Python API endpoint saved as `$PYTHON_URL`.
- (Local mode only: Docker running, Cosmos DB emulator optional.) Labs 4–6 assume Azure is
  available. If running locally, the API falls back to `data/*.json` for read-only demos.

---

## Background — data agents

| Agent | Primary data store | Tools |
|-------|--------------------|-------|
| `merchandiser` | Cosmos DB `products`, `reviews`; PostgreSQL analytics | `search_products`, `get_reviews`, `sales_trends` |
| `operations` | Cosmos DB `orders`, `customers`; Document Intelligence | `get_inventory`, `parse_supplier_doc`, `restock_suggestion` |

Cosmos DB uses **AAD RBAC** (key-auth disabled) with the Managed Identity
(`AZURE_CLIENT_ID`). The `DefaultAzureCredential` chain resolves the credential in both
Container Apps (production) and your dev container (developer credential).

---

## Step 1 — Query the merchandiser agent

### Search products

=== "Python"

    ```bash
    curl -s -X POST $PYTHON_URL/chat \
      -H "Content-Type: application/json" \
      -d '{
        "message": "Show me the top smart running products under $200.",
        "agent": "merchandiser"
      }' | python -m json.tool
    ```

=== ".NET"

    ```bash
    $DOTNET_URL = (azd env get-values | Select-String "SERVICE_API_DOTNET_ENDPOINT").ToString().Split('=')[1]
    curl -s -X POST "$DOTNET_URL/chat" `
      -H "Content-Type: application/json" `
      -d '{"message":"Show me smart running products under $200.","agent":"merchandiser"}' `
      | python -m json.tool
    ```

Expected: a list of products from `data/products.json` / Cosmos DB `products` container.

### Get product reviews

```bash
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What do customers say about the ZP-001 connected running shirt?",
    "agent": "merchandiser"
  }' | python -m json.tool
```

Expected: review summary with average rating from `data/reviews.json`.

### Sales trends

```bash
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Which product categories have been trending in the last 30 days?",
    "agent": "merchandiser"
  }' | python -m json.tool
```

---

## Step 2 — Query the operations agent

### Inventory check

```bash
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the current inventory level for the ZP-003 recovery leggings?",
    "agent": "operations"
  }' | python -m json.tool
```

### Restock suggestion

```bash
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Which products need restocking? Suggest reorder quantities.",
    "agent": "operations"
  }' | python -m json.tool
```

Expected: list of low-stock items from Cosmos DB with suggested reorder quantities.

---

## Step 3 — Parse a supplier document (Document Intelligence)

The `operations` agent's `parse_supplier_doc` tool calls **Azure Document Intelligence** to extract
structured data from PDF/MD supplier documents in `data/suppliers/`.

```bash
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Parse the latest supplier invoice for SUP-001 and extract the line items.",
    "agent": "operations"
  }' | python -m json.tool
```

Expected response includes structured fields extracted by Document Intelligence:

```json
{
  "reply": "Supplier SUP-001 invoice dated 2025-06-01 contains 3 line items: ...",
  "agent": "operations",
  "citations": [
    { "source": "data/suppliers/sup-001-invoice.md", "chunk": "LINE ITEM: ZP-001 × 500 @ $45", "score": 1.0 }
  ],
  "traceId": "..."
}
```

!!! tip "Local mode"
    Without Azure, `parse_supplier_doc` returns a stub response derived from the Markdown files
    in `data/suppliers/`. The full Document Intelligence path requires `AZURE_DOCINTEL_ENDPOINT`.

---

## Step 4 — Customer diversity: query by business unit (B.2.2)

The three Zava business units are modelled as `customers` in Cosmos DB. Query each:

```bash
# Retail Stores orders
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show orders for Zava Retail Stores.", "agent": "operations"}' \
  | python -m json.tool

# eCommerce orders
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show orders for Zava eCommerce.", "agent": "operations"}' \
  | python -m json.tool

# Wholesale orders
curl -s -X POST $PYTHON_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show orders for Zava Wholesale.", "agent": "operations"}' \
  | python -m json.tool
```

Notice that each business unit has distinct order patterns — this is the **customer diversity**
data that maps to B.2.2 evidence.

---

## Step 5 — Trace a Cosmos DB query

1. Run the inventory query from Step 2 and note the `traceId`.
2. In Application Insights → **Transaction search**, paste the `traceId`.
3. Expand the trace to see the Cosmos DB dependency call (duration, RU charge, status code).
4. Screenshot the trace tree.

=== "Python"

    The Cosmos DB SDK emits OpenTelemetry spans automatically when
    `APPLICATIONINSIGHTS_CONNECTION_STRING` is set.

=== ".NET"

    The `Microsoft.Azure.Cosmos` client emits distributed tracing spans compatible with
    Application Insights.

---

## Step 6 — Explore the data model

Inspect the Cosmos DB containers directly:

```bash
# Using Azure CLI
az cosmosdb sql container list \
  --account-name cosmos-zava-dev \
  --database-name zava \
  --resource-group rg-zava-dev \
  --output table
```

Confirm three containers: `products`, `orders`, `customers`.

Query a document:

```bash
az cosmosdb sql query \
  --account-name cosmos-zava-dev \
  --database-name zava \
  --name products \
  --resource-group rg-zava-dev \
  --query-text "SELECT TOP 3 c.id, c.name, c.price FROM c"
```

---

## Validation checklist

- [ ] `merchandiser` agent returns products with prices from Cosmos DB.
- [ ] `merchandiser` agent returns review summary for `ZP-001`.
- [ ] `operations` agent returns inventory levels and restock suggestions.
- [ ] `parse_supplier_doc` extracts line items from `data/suppliers/`.
- [ ] Three business-unit queries return distinct order sets (B.2.2).
- [ ] Cosmos DB span visible in Application Insights trace tree.
- [ ] Cosmos DB key-auth confirmed disabled (`az cosmosdb show ... | grep disableLocalAuth`).

---

## Evidence checkpoint — B.1.1, B.2.1, B.2.2

| Artifact | What it proves | Control |
|----------|---------------|---------|
| Operations agent parsing a supplier doc | Document Intelligence in AI Services pillar | B.1.1 |
| Cosmos DB + PostgreSQL holding Zava data | Data pillar coverage | B.2.1 |
| Three distinct business-unit queries | Customer diversity (Retail, eCommerce, Wholesale) | B.2.2 |
| Application Insights trace of Cosmos query | End-to-end observability on Data pillar | B.2.1 |

> **Action:** Save the business-unit query outputs as `evidence/b22-business-unit-queries-lab4.txt`
> and the Application Insights trace screenshot as `evidence/b21-cosmos-trace-lab4.png`.

---

## Key concepts review

| Concept | Detail |
|---------|--------|
| `merchandiser` tools | `search_products`, `get_reviews`, `sales_trends` — Cosmos DB + pgvector |
| `operations` tools | `get_inventory`, `parse_supplier_doc`, `restock_suggestion` |
| Cosmos DB RBAC | `disableLocalAuth: true`; MI has `Cosmos DB Built-in Data Contributor` |
| Document Intelligence | Extracts structured fields from supplier PDFs/Markdown |
| Customer diversity | Three Cosmos DB `customers` docs = three B.2.2 entities |
| pgvector `reviews` | Optional — reviews can also be stored in PostgreSQL for vector similarity |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ResourceNotFound` for Cosmos container | Run `seed.py --target azure` to create containers |
| `parse_supplier_doc` returns stub | Set `AZURE_DOCINTEL_ENDPOINT`; check MI has `Cognitive Services User` role |
| Cosmos DB 403 | Ensure `AZURE_CLIENT_ID` set; MI has data-plane role on the account |
| No Cosmos span in App Insights | Confirm `APPLICATIONINSIGHTS_CONNECTION_STRING` is set in Container App |

## Next lab

Proceed to **[Lab 5 — Trust, safety & observability](lab5.md)**.
