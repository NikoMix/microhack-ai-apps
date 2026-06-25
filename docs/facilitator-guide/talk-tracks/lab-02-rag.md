# Talk Track — Lab 2: Ground It (RAG)

**Block:** Grounding & RAG (10:55–11:10) + Lab 2 (11:10–12:00)
**Slides:** Section 5 of `slides/zava-microhack-deck.md`
**Lab guide:** `docs/labs/lab-02-rag.md`
**Duration:** 15 min lecture + 50 min lab

---

## Grounding & RAG Lecture (10:55–11:10, 15 min)

### The problem: hallucination (3 min)

Start with the pain:

> "Without grounding, ask the agent 'What is Zava's return policy?' and the model
> will make something up — confidently. It might say '60 days' when the real answer
> is '30 days from purchase'. That's a hallucination, and in enterprise settings it
> erodes trust fast."

Show what a grounded response looks like vs an ungrounded one:

- **Ungrounded:** "Zava accepts returns within 60 days." (no evidence)
- **Grounded:** "Zava accepts returns within 30 days of purchase. [Source: policies/returns.md]"

### The RAG pipeline (5 min)

Walk through the pipeline slide:

```text
User query → Embed query → Vector search → Top-k chunks → Augmented prompt → LLM → Reply + citations
```

Key points:

1. **Embedding** converts text to a 1536-dimensional vector (using `text-embedding-3-small`)
2. **Vector search** finds the semantically closest chunks in the knowledge store
3. **Top-k chunks** are appended to the LLM prompt as context
4. **Citations** come from the metadata of the retrieved chunks (source file + excerpt)

> "The model doesn't call the database — the `search_knowledge` tool does. The model just receives
> the retrieved text as part of its context. This is RAG: Retrieval-Augmented Generation."

### Two knowledge stores (3 min)

**Azure AI Search (default for production):**

- Managed service; supports hybrid search (keyword + vector)
- Index name: `zava-knowledge`
- Vector dimension: `1536` (must match `text-embedding-3-small`)
- Ingested from: `data/policies/*.md`, `data/products.json`, `data/reviews.json`

**pgvector (for Postgres-first teams):**

```sql
SELECT content, source, embedding <=> $1::vector AS distance
FROM knowledge ORDER BY distance LIMIT 5;
```

> "Same SQL database, vector extension. Great if your team already runs PostgreSQL
> and doesn't want another managed service."

### Provider swap demo (4 min)

This is the key demo for Lab 2 — do it live:

```bash
# Default: GitHub Models
INFERENCE_PROVIDER=github
# Start API, make a query, show the response

# Swap to Azure AI Foundry
INFERENCE_PROVIDER=foundry
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=<your endpoint>
# Restart API, same query, same response — different backend
```

> "This is the modular inference pattern in action. The agents don't change. The tools
> don't change. The HTTP API doesn't change. Only one environment variable changes."

---

## Lab 2 (11:10–12:00, 50 min)

### Expected lab flow

1. Attendees index Zava policies and catalog into Azure AI Search (or pgvector locally)
2. They upgrade `ConciergeAgent.search_knowledge` to query the index
3. They verify citations appear in the response JSON
4. They swap `INFERENCE_PROVIDER` and confirm the same behaviour

### Demo cue — citations in action

Before releasing attendees, show this expected output:

```json
{
  "reply": "Zava's returns policy allows returns within 30 days of purchase...",
  "agent": "concierge",
  "citations": [
    {
      "source": "policies/returns.md",
      "chunk": "Returns are accepted within 30 days of the original purchase date..."
    }
  ],
  "traceId": "a2f3b..."
}
```

### Watch for

- **Embedding dimension mismatch** — if the index was created with a different dimension,
  queries will fail. Confirm `vector(1536)` in the schema matches the embedding model.
- **Missing `EMBEDDINGS_PROVIDER`** — attendees may forget to set this. Default is `github`.
- **AI Search auth** — if using Azure AI Search, confirm the Managed Identity or API key
  is configured. (In local dev, the shared access key from `.env` is acceptable.)
- **pgvector extension not installed** — if using PostgreSQL locally, run `CREATE EXTENSION vector;`

### Evidence checkpoint

> "Citations in your response = grounded agent. Screenshot that JSON response — it's
> evidence for B.1.1 (grounded AI capability). If you also swapped to Azure AI Foundry,
> note the endpoint you used — that's your first Azure AI Services touchpoint for B.2.1."

### Fallback

If AI Search indexing fails, attendees can use the pgvector path locally (no Azure needed).
Point them to the solution at `docs/solutions/lab-02/`.

---

## Common questions during Lab 2

**Q: How is this different from just giving the LLM all the documents in the prompt?**

> "At scale, you have thousands of policy documents, millions of product records, years
> of reviews. You can't fit all of that in a context window — and even if you could,
> it would be expensive and slow. RAG retrieves only the relevant pieces, at query time,
> cheaply. The model only ever sees what it needs."

**Q: Why 1536 dimensions specifically?**

> "`text-embedding-3-small` produces 1536-dimensional vectors. The vector store's schema
> must match the embedding model's output dimension exactly. If you switch models,
> you must re-index with the new model. This is pinned in the build contract so everyone
> uses the same dimension and the schema doesn't drift."

**Q: What's the difference between Azure AI Search and pgvector?**

> "Azure AI Search is a fully managed service with built-in chunking, enrichment pipelines,
> and hybrid search. pgvector is a PostgreSQL extension — it's simpler, self-managed, and
> great if you already run PostgreSQL. For this microhack, both work. In production,
> choose based on your scale, team expertise, and existing infrastructure."

**Q: Can I use Bing or another search engine?**

> "Not in this microhack — we don't use Bing or any external search. All knowledge is
> indexed from the `data/` directory so the platform is self-contained and auditable.
> In a real engagement you'd connect to your customer's SharePoint, databases, or other
> internal knowledge stores."
