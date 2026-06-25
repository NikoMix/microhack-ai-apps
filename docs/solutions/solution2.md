# Solution 2 — Ground It: RAG over Zava Knowledge

> **Facilitator note:** The key validation is that `citations` is non-empty and points to the
> correct policy file. Dimension mismatch errors are the #1 failure mode — remind students the
> embedding model must always produce 1536-dim vectors.

## Expected command outputs

### Database initialisation and seeding

```text
Seeding knowledge from data/policies/ ...
Embedded: returns.md          (4 chunks)
Embedded: warranty.md         (3 chunks)
Embedded: sizing.md           (5 chunks)
Embedded: sustainability.md   (6 chunks)
Embedded: smart-garment-care.md (4 chunks)
Total: 22 chunks inserted into pgvector.
```

Verify the database:

```bash
psql -h localhost -U postgres -d zava -c "SELECT count(*) FROM knowledge;"
```

```text
 count
-------
    22
(1 row)
```

### Return policy query with citations

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the Zava return policy for smart garments?", "agent": "concierge"}' \
  | python -m json.tool
```

```json
{
  "reply": "Zava's return policy allows returns within 90 days for smart garments, provided the embedded sensor module is intact and the item is unworn and unwashed. Returns can be initiated online or at any Zava Retail Store. Please retain the original packaging for sensor module returns.",
  "agent": "concierge",
  "citations": [
    {
      "source": "data/policies/returns.md",
      "chunk": "Smart garments may be returned within 90 days of purchase provided the integrated sensor module remains intact and undamaged.",
      "score": 0.94
    },
    {
      "source": "data/policies/returns.md",
      "chunk": "Returns can be processed via our online portal or at any Zava Retail Store location.",
      "score": 0.88
    }
  ],
  "traceId": "5e6f1a2b3c4d5e6f1a2b3c4d5e6f1a2b"
}
```

### Warranty query

```json
{
  "reply": "Zava smart garments come with a 2-year limited warranty covering manufacturing defects and sensor module failures under normal use. Physical damage and wear-and-tear are excluded.",
  "agent": "concierge",
  "citations": [
    {
      "source": "data/policies/warranty.md",
      "chunk": "Smart garments carry a 2-year limited warranty from the date of purchase...",
      "score": 0.96
    }
  ],
  "traceId": "6f1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c"
}
```

### Sustainability query

```json
{
  "reply": "Zava uses recycled polyester (rPET) and bio-based nylon in all smart garments. The sensor modules are designed for end-of-life recycling through the Zava Return-to-Recycle programme.",
  "agent": "concierge",
  "citations": [
    {
      "source": "data/policies/sustainability.md",
      "chunk": "Zava smart garments are constructed from ≥50% recycled materials (rPET and bio-based nylon)...",
      "score": 0.91
    }
  ],
  "traceId": "1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d"
}
```

## pgvector schema (facilitator reference)

```sql
-- Expected table definition
\d knowledge;
```

```text
                     Table "public.knowledge"
   Column    |         Type          | Nullable |
-------------+-----------------------+----------+
 id          | uuid                  | not null |
 source      | text                  | not null |
 chunk       | text                  | not null |
 embedding   | vector(1536)          | not null |
 created_at  | timestamp             |          |
```

_The `vector(1536)` column is the critical evidence for B.2.1 (Data pillar + 1536-dim contract)._

## Filled evidence artifacts

### b11-rag-citations-lab2.png

_Screenshot showing the `/chat` response with `citations` array containing `returns.md` source
and score 0.94+. The non-empty citations array is the key indicator that RAG is working._

### b21-pgvector-seed-lab2.txt

```text
Environment: EMBEDDINGS_PROVIDER=github
Model: openai/text-embedding-3-small
Endpoint: https://models.github.ai/inference
Dimension: 1536

Seeded 22 chunks into PostgreSQL pgvector
Table: public.knowledge (vector(1536))
Database: zava @ localhost:5432

Verification:
SELECT count(*) FROM knowledge; → 22
SELECT length(embedding) FROM knowledge LIMIT 1; → 1536
```

## Common failure modes

| Failure | Root cause | Fix |
|---------|-----------|-----|
| `citations: []` after seeding | Query vector and DB vectors produced by different models | Reseed with the same `EMBEDDINGS_PROVIDER` as inference |
| `extension "vector" does not exist` | pgvector not installed | `CREATE EXTENSION vector;` as postgres superuser |
| Dimension mismatch on insert | Wrong model returning 768-dim | Confirm `GITHUB_MODELS_EMBEDDING_MODEL=openai/text-embedding-3-small` |
| Low citation scores (< 0.5) | Mismatched chunking strategy | Check chunk size (target 256–512 tokens); reseed |
