# Talk Track — Lab 4: Data Agents

**Block:** Data Agents lecture (14:00–14:15) + Lab 4 (14:15–15:00)
**Slides:** Section 7 of `slides/zava-microhack-deck.md`
**Lab guide:** `docs/labs/lab-04-data-agents.md`
**Duration:** 15 min lecture + 45 min lab

---

## Data Agents Lecture (14:00–14:15, 15 min)

### Why data grounding? (3 min)

> "In Lab 2 we grounded the Concierge on documents — policies, product descriptions, reviews.
> Now we go deeper: the Merchandiser and Operations agents need *live data* from Cosmos DB
> and PostgreSQL. Product inventory, order history, supplier docs. This is where the
> Data pillar of the Advanced Specialization comes alive."

Remind attendees of the pillar → service mapping:

- Data pillar: **Cosmos DB** + **PostgreSQL Flexible Server**
- Both addressed in today's lab

### Cosmos DB schema (5 min)

Show the three containers:

| Container | Key fields | Agent |
|---|---|---|
| `products` | id, name, category, price, smart-features | Merchandiser |
| `orders` | orderId, customer, items, status | Concierge |
| `customers` | id, businessUnit, associationType | Orchestrator |

Key teaching points:

1. **No keys** — `disableLocalAuth: true` in the Bicep template. The Container App's Managed Identity has the `Cosmos DB Built-in Data Reader` and `Cosmos DB Built-in Data Contributor` roles.
2. **Local dev** — use the Azure Cosmos DB emulator bundled in the dev container, or the real Cosmos DB after `azd up`.
3. **Document model** — Cosmos DB is schema-flexible. The `products` container holds JSON documents matching `data/products.json`.

Show a quick query:

```python
# Merchandiser: get_reviews tool
async def get_reviews(self, product_id: str) -> list[dict]:
    query = "SELECT * FROM c WHERE c.productId = @id"
    items = self.cosmos.query_items(
        container="products",
        query=query,
        parameters=[{"name": "@id", "value": product_id}]
    )
    return [item async for item in items]
```

### PostgreSQL + pgvector recap (4 min)

Link back to Lab 2 — the knowledge store uses pgvector for semantic search. But PostgreSQL
also stores structured data:

- **Operations agent** can query inventory levels directly via SQL
- **Concierge** can look up order history via a SQL join

```sql
-- Operations: get_inventory tool
SELECT product_id, name, stock_level, warehouse
FROM   inventory
WHERE  stock_level < reorder_threshold
ORDER  BY stock_level ASC;
```

> "PostgreSQL is both a **vector knowledge store** (pgvector extension) and a
> **relational data store**. One database, two roles. That's why it sits in the
> Data pillar and satisfies B.2.1."

### Introduce Lab 4 (3 min)

> "In this lab you'll implement the Merchandiser and Operations agents. Each has
> 2–3 tools backed by Cosmos DB. You'll test with sample queries and confirm the
> Orchestrator routes correctly. The key outcome: data from your Azure resources
> flows through an agent to a user's question."

---

## Lab 4 (14:15–15:00, 45 min)

### Expected lab flow

1. Attendees implement `MerchandiserAgent` with `search_products`, `get_reviews`, `sales_trends`
2. They implement `OperationsAgent` with `get_inventory`, `parse_supplier_doc`, `restock_suggestion`
3. They register both agents with the Orchestrator
4. They test routing with sample queries
5. Faster attendees explore the Document Intelligence integration (`parse_supplier_doc`)

### Sample test queries

Have attendees test these queries:

```bash
# Should route to Merchandiser
curl -X POST http://localhost:8000/chat \
  -d '{"message": "Show me reviews for the Zava Alpha leggings"}'

# Should route to Operations
curl -X POST http://localhost:8000/chat \
  -d '{"message": "Which running shirts are low in stock?"}'

# Should use restock_suggestion
curl -X POST http://localhost:8000/chat \
  -d '{"message": "Generate a restock report for our top products"}'
```

### Watch for

- **Orchestrator not routing correctly** — check the Orchestrator's system prompt. It should describe Merchandiser and Operations clearly. If the model keeps routing to Concierge, the system prompt is ambiguous.
- **Cosmos DB connection** — after `azd up`, the `COSMOS_ENDPOINT` env var should be set. If not, run `azd env get-values` and set it manually.
- **Document Intelligence timeout** — the `parse_supplier_doc` tool makes an async call to Document Intelligence. If the service isn't provisioned, use the mock implementation in the lab guide.
- **.NET async patterns** — .NET attendees may struggle with `async/await` chains in tool implementations. The solution branch has the complete pattern.

### Demo cue — Document Intelligence

If time permits, show the `parse_supplier_doc` tool in action:

```bash
# This query triggers the Operations agent to parse a supplier PDF
curl -X POST http://localhost:8000/chat \
  -d '{"message": "Parse the delivery note from TechFiber Corp"}'
```

Show in Application Insights: the trace includes a call to Document Intelligence.

> "Document Intelligence extracts structured data from PDFs, Word docs, and scanned images.
> The Operations agent uses it to ingest supplier documents that arrive in non-structured formats."

### Evidence checkpoint

> "Two new agents, Cosmos DB integration, PostgreSQL queries. Screenshot the
> Orchestrator routing a Merchandiser query and an Operations query to the right agents.
> That's B.1.1 (AI on Azure) + B.2.1 (Data pillar: Cosmos DB and PostgreSQL) evidence.
> Note: the Zava business units using these agents (Retail, eCommerce, Wholesale) are
> the B.2.2 customer-diversity evidence."

---

## Common questions during Lab 4

**Q: Why Cosmos DB for products/orders but PostgreSQL for knowledge?**

> "Cosmos DB is optimised for high-throughput, schema-flexible document operations —
> great for products and orders that have variable shapes (smart shirts have different
> fields than leggings). PostgreSQL is perfect for structured data and, with pgvector,
> for embeddings. Using both covers the Data pillar breadth that B.2.1 expects."

**Q: What is Document Intelligence used for?**

> "Zava's Operations team receives supplier documents as PDFs and Word files. Document
> Intelligence extracts the structured data — delivery notes, spec sheets, invoices —
> so the Operations agent can answer questions like 'Has the TechFiber shipment arrived?'
> without a human manually parsing the document."

**Q: How does `sales_trends` work without a real analytics database?**

> "In the lab, `sales_trends` queries the Cosmos DB `orders` container and aggregates
> on the client side. In production you'd connect to a dedicated analytics store — Azure
> Synapse Analytics or Fabric Lakehouse. For today, the Cosmos query is sufficient to
> demonstrate the pattern."
