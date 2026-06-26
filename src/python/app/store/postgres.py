"""
PostgreSQL / pgvector helper — schema management and batch upsert.

The knowledge table stores chunked policy and supplier content with
1536-dimension embeddings (text-embedding-3-small).

Used by seed.py to populate the knowledge base.
Schema is also referenced by AzureZavaStore.search_knowledge.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# DDL — run once during seed or startup
CREATE_KNOWLEDGE_TABLE = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS knowledge (
    id          TEXT PRIMARY KEY,
    source      TEXT NOT NULL,      -- e.g. "policies/returns.md"
    title       TEXT NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(1536),       -- text-embedding-3-small
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS knowledge_embedding_idx
    ON knowledge USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 50);
"""


async def ensure_schema(pool: Any) -> None:
    """Create the knowledge table if it doesn't exist."""
    async with pool.acquire() as conn:
        await conn.execute(CREATE_KNOWLEDGE_TABLE)
    logger.info("PostgreSQL schema ready")


async def upsert_knowledge(
    pool: Any,
    records: list[dict[str, Any]],
) -> None:
    """Upsert knowledge records into the knowledge table.

    Each record must have: id, source, title, content, embedding (list[float]).
    """
    if not records:
        return

    async with pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO knowledge (id, source, title, content, embedding)
            VALUES ($1, $2, $3, $4, $5::vector)
            ON CONFLICT (id) DO UPDATE SET
                source    = EXCLUDED.source,
                title     = EXCLUDED.title,
                content   = EXCLUDED.content,
                embedding = EXCLUDED.embedding
            """,
            [
                (
                    r["id"],
                    r["source"],
                    r["title"],
                    r["content"],
                    r["embedding"],
                )
                for r in records
            ],
        )
    logger.info("Upserted %d knowledge records", len(records))
