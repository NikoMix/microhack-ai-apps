# Lab 2 — Ground It: RAG over Zava Knowledge

> **Estimated time:** 50 minutes
> **Module B controls:** B.1.1 (Azure AI Implementation), B.2.1 (ACR Performance — Data & AI pillars),
> B.3.1 (Certifications)

## Learning objectives

By the end of this lab you will be able to:

1. Embed Zava knowledge documents (policies, product descriptions) with `text-embedding-3-small`
   (1536-dim).
2. Load embeddings into **PostgreSQL pgvector** and/or **Azure AI Search** (`zava-knowledge` index).
3. Issue RAG-grounded queries through the `concierge` agent's `search_knowledge` tool.
4. Inspect citations in the `/chat` response.
5. Switch `EMBEDDINGS_PROVIDER` from `github` to `azure-openai` or `foundry`.

## Prerequisites

- Lab 1 complete — API running, agents working.
- **PostgreSQL** available. The dev container starts a local PostgreSQL 16 instance with the
  `pgvector` extension automatically. If using Codespaces, it is already running.

---

## Background — RAG in Zava

Zava knowledge lives in `data/policies/*.md` and the product catalog. The `concierge` agent calls
`search_knowledge(query)` which:

1. Embeds the query with `text-embedding-3-small` (**1536 dimensions**).
2. Runs a vector similarity search against PostgreSQL `pgvector` (`vector(1536)`) and/or Azure
   AI Search (index `zava-knowledge`, field dimension 1536).
3. Returns the top-k chunks as `citations` in the API response.

The **embedding dimension must be 1536** across all providers — this is set in the build contract
and cannot change.

---

## Step 1 — Verify PostgreSQL is running

```bash
psql -h localhost -U postgres -d zava -c "\dt"
```

If the database does not exist yet, run the init script:

=== "Python"

    ```bash
    cd src/python
    python scripts/init_db.py
    ```

=== ".NET"

    ```bash
    cd src/dotnet
    dotnet run --project ZavaApi -- --init-db
    ```

Expected output includes a `knowledge` table with a `vector(1536)` column.

---

## Step 2 — Seed the knowledge base

Load Zava policy documents and embed them. This uses `EMBEDDINGS_PROVIDER=github` (free):

=== "Python"

    ```bash
    cd src/python
    python scripts/seed_knowledge.py
    ```

    Expected output:

    ```
    Seeding knowledge from data/policies/ ...
    Embedded: returns.md          (4 chunks)
    Embedded: warranty.md         (3 chunks)
    Embedded: sizing.md           (5 chunks)
    Embedded: sustainability.md   (6 chunks)
    Embedded: smart-garment-care.md (4 chunks)
    Total: 22 chunks inserted into pgvector.
    ```

=== ".NET"

    ```bash
    cd src/dotnet
    dotnet run --project ZavaApi -- --seed-knowledge
    ```

    Expected output:

    ```
    [Seed] Loading documents from data/policies/
    [Seed] Embedded 22 chunks → PostgreSQL pgvector (vector(1536))
    ```

!!! note "Embedding provider"
    With `EMBEDDINGS_PROVIDER=github` the script calls the GitHub Models embeddings endpoint:
    `https://models.github.ai/inference` with model `openai/text-embedding-3-small`. This is
    OpenAI-compatible and returns 1536-dimensional vectors.

---

## Step 3 — Query with citations

Now ask the concierge a policy question and verify citations are returned:

=== "Python"

    ```bash
    curl -s -X POST http://localhost:8000/chat \
      -H "Content-Type: application/json" \
      -d '{
        "message": "What is the Zava return policy for smart garments?",
        "agent": "concierge"
      }' | python -m json.tool
    ```

=== ".NET"

    ```bash
    curl -s -X POST http://localhost:8080/chat \
      -H "Content-Type: application/json" \
      -d "{
        \"message\": \"What is the Zava return policy for smart garments?\",
        \"agent\": \"concierge\"
      }" | python -m json.tool
    ```

Expected response includes non-empty `citations`:

```json
{
  "reply": "Zava's return policy allows returns within 90 days for unworn items...",
  "agent": "concierge",
  "citations": [
    {
      "source": "data/policies/returns.md",
      "chunk": "Smart garments may be returned within 90 days...",
      "score": 0.92
    }
  ],
  "traceId": "..."
}
```

---

## Step 4 — Test multiple policy queries

Run these queries and note the citations each time:

```bash
# Warranty
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Is my smart running shirt covered under warranty?", "agent": "concierge"}' \
  | python -m json.tool

# Sizing
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I find the right size Zava jacket?", "agent": "concierge"}' \
  | python -m json.tool

# Sustainability
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What materials does Zava use for sustainability?", "agent": "concierge"}' \
  | python -m json.tool
```

---

## Step 5 (optional) — Load Azure AI Search index

If you have an Azure subscription and want to seed the `zava-knowledge` AI Search index:

1. Set these additional env vars (or get them from `azd env get-values` after Lab 3):

    ```dotenv
    AZURE_SEARCH_ENDPOINT=https://YOUR_SEARCH_SERVICE.search.windows.net
    AZURE_SEARCH_INDEX=zava-knowledge
    ```

2. Run the seeder with the Azure target:

    === "Python"

        ```bash
        AZURE_SEARCH_TARGET=true python scripts/seed_knowledge.py
        ```

    === ".NET"

        ```bash
        dotnet run --project ZavaApi -- --seed-knowledge --target azure-search
        ```

    The script creates the index with field `content_vector` of dimension **1536** and populates it.

!!! info "AI Search vector field"
    The Azure AI Search index schema uses `Edm.Single` vector fields with `dimensions: 1536` and
    `vectorSearchAlgorithm: hnsw`. This matches the `text-embedding-3-small` output dimension.

---

## Step 6 — Switch embeddings provider

To verify the provider abstraction, switch to Azure OpenAI embeddings (requires Azure subscription):

```dotenv
EMBEDDINGS_PROVIDER=azure-openai
AZURE_OPENAI_ENDPOINT=https://YOUR_ACCOUNT.openai.azure.com
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

Re-run a knowledge query. The response should be identical — only the embedding computation
changes. The 1536-dim contract is preserved across all providers.

!!! info "Foundry embeddings"
    To use Azure AI Foundry: `EMBEDDINGS_PROVIDER=foundry`. The `AIProjectClient` resolves
    the embeddings endpoint from `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT`.

---

## Validation checklist

- [ ] `pgvector` knowledge table populated with 22 chunks.
- [ ] `POST /chat` with a policy question returns at least one `citations` entry.
- [ ] Citation `source` matches a file in `data/policies/`.
- [ ] Citation `score` is between 0.0 and 1.0.
- [ ] Re-seeding with a different `EMBEDDINGS_PROVIDER` produces the same query results.

---

## Evidence checkpoint — B.1.1, B.2.1

| Artifact | What it proves | Control |
|----------|---------------|---------|
| Screenshot: citations in `/chat` response | RAG capability — AI Services + Data pillar | B.1.1 |
| Seed script output (22 chunks, 1536-dim) | `text-embedding-3-small` deployed on Azure AI | B.1.1 |
| pgvector `vector(1536)` schema | Azure Database for PostgreSQL + pgvector in Data pillar | B.2.1 |
| AI Search index `zava-knowledge` (if created) | Azure AI Search in AI Services pillar | B.2.1 |

> **Action:** Save the citations screenshot as `evidence/b11-rag-citations-lab2.png` and the seed
> output as `evidence/b21-pgvector-seed-lab2.txt`.

---

## Key concepts review

| Concept | Detail |
|---------|--------|
| Embedding dimension | 1536 — fixed for `text-embedding-3-small` across all providers |
| pgvector | PostgreSQL extension; column type `vector(1536)` |
| AI Search index | `zava-knowledge`; HNSW algorithm; field dimension 1536 |
| `search_knowledge` tool | Embeds query → vector search → returns top-k chunks |
| Citations | `[{source, chunk, score}]` in every RAG response |
| `EMBEDDINGS_PROVIDER` | Independent from `INFERENCE_PROVIDER` — mix and match |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `psql: could not connect` | Check `POSTGRES_HOST=localhost`, PostgreSQL service running |
| `extension "vector" does not exist` | Run `CREATE EXTENSION vector;` as superuser |
| `citations: []` after seeding | Ensure seeder ran successfully; check `knowledge` table row count |
| Dimension mismatch error | All providers must produce 1536-dim; check model name |
| AI Search 403 | Use `DefaultAzureCredential`; ensure `AZURE_SEARCH_DATA_CONTRIBUTOR` role |

## Next lab

Proceed to **[Lab 3 — Deploy to Azure with azd](lab3.md)**.
