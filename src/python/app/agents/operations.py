"""
Operations agent — supply chain, inventory management, supplier doc parsing.

Tools (build-contract §2):
  - get_inventory(product_id)           → current stock levels
  - parse_supplier_doc(doc_id)          → extract key fields from supplier docs
  - restock_suggestion(threshold)       → identify products needing restock

In Azure mode, parse_supplier_doc uses Azure Document Intelligence.
In local/github mode, it reads the markdown supplier docs directly.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from agent_framework import Agent, tool

from app.agents.concierge import _add_citation
from app.store.base import ZavaStore

logger = logging.getLogger(__name__)


def make_operations_agent(
    client: Any,
    store: ZavaStore,
    docintel_endpoint: str = "",
    azure_client_id: str = "",
) -> Agent:
    """Return a configured Operations agent.

    Parameters
    ----------
    client:
        Chat inference client.
    store:
        Zava data store (local or Azure).
    docintel_endpoint:
        Azure Document Intelligence endpoint. If empty, uses local markdown parsing.
    azure_client_id:
        User-assigned Managed Identity client ID for Document Intelligence.
    """

    @tool
    async def get_inventory(product_id: str = "") -> str:
        """Return current inventory levels for Zava products.

        Parameters
        ----------
        product_id:
            Optional product ID to filter (e.g., ZAVA-RUN-001).
            Omit or pass empty string to get all products.
        """
        inventory = await store.get_inventory(product_id=product_id or None)
        if not inventory:
            return "No inventory data found."
        _add_citation(
            source="inventory/current",
            title="Zava Inventory",
            excerpt=f"{len(inventory)} products tracked",
        )
        return json.dumps(inventory, indent=2)

    @tool
    async def parse_supplier_doc(doc_id: str) -> str:
        """Extract structured information from a Zava supplier document.

        In Azure mode, uses Azure Document Intelligence to parse PDFs.
        In local mode, reads the markdown supplier files.

        Parameters
        ----------
        doc_id:
            Supplier document identifier (e.g., "invoice-flexcircuit-88231",
            "po-smarttextile-2026-04417").
        """
        if docintel_endpoint:
            return await _parse_with_document_intelligence(
                doc_id, docintel_endpoint, azure_client_id
            )
        return await _parse_local_supplier_doc(doc_id, store)

    @tool
    async def restock_suggestion(threshold: int = 100) -> str:
        """Identify products with stock below a given threshold and suggest restock quantities.

        Parameters
        ----------
        threshold:
            Minimum acceptable stock level. Products below this will be flagged.
            Default is 100 units.
        """
        inventory = await store.get_inventory()
        low_stock = [item for item in inventory if item.get("inStock", 0) < threshold]
        if not low_stock:
            return f"All products have stock at or above {threshold} units. No restock needed."

        suggestions = []
        for item in sorted(low_stock, key=lambda x: x.get("inStock", 0)):
            current = item.get("inStock", 0)
            # Suggest restocking to 2x threshold
            suggested_qty = max(threshold * 2 - current, 50)
            suggestions.append(
                {
                    "productId": item["productId"],
                    "name": item["name"],
                    "currentStock": current,
                    "suggestedRestock": suggested_qty,
                    "urgency": "HIGH" if current < threshold * 0.3 else "MEDIUM",
                }
            )

        _add_citation(
            source="inventory/restock-analysis",
            title="Restock Suggestions",
            excerpt=f"{len(suggestions)} products below threshold {threshold}",
        )
        return json.dumps(
            {"threshold": threshold, "suggestions": suggestions},
            indent=2,
        )

    instructions = """You are the Zava Operations Manager — responsible for supply chain health,
inventory visibility, and supplier relationship data.

Your capabilities:
- Check real-time inventory levels via get_inventory
- Parse and extract key data from supplier invoices and purchase orders via parse_supplier_doc
- Identify restock needs and generate procurement suggestions via restock_suggestion

Guidelines:
- Flag low-stock items proactively (especially for high-rated or high-demand products)
- When parsing supplier docs, extract: supplier name, amounts, line items, due dates
- Restock suggestions should factor in urgency (items below 30% of threshold are HIGH priority)
- Cross-reference inventory with sales trends when possible
- Escalate supply chain risks clearly with actionable next steps
"""

    return Agent(
        name="operations",
        instructions=instructions,
        tools=[get_inventory, parse_supplier_doc, restock_suggestion],
        client=client,
    )


# ── Document parsing helpers ──────────────────────────────────────────────────


async def _parse_local_supplier_doc(doc_id: str, store: ZavaStore) -> str:
    """Parse a supplier doc from the local markdown store."""
    doc = await store.get_supplier_doc(doc_id)
    if doc is None:
        return (
            f"Supplier document {doc_id!r} not found. "
            "Available docs: invoice-flexcircuit-88231, po-smarttextile-2026-04417"
        )

    content = doc["content"]
    extracted = _extract_supplier_fields(content, doc["source"])
    _add_citation(
        source=doc["source"],
        title=doc["title"],
        excerpt=content[:200],
    )
    return json.dumps(extracted, indent=2)


def _extract_supplier_fields(content: str, source: str) -> dict[str, Any]:
    """Extract structured fields from a supplier markdown document."""
    fields: dict[str, Any] = {"source": source, "rawExcerpt": content[:300]}

    # Common patterns in supplier docs
    patterns = {
        "supplierName": r"(?:Supplier|Vendor):\s*(.+)",
        "invoiceNumber": r"Invoice Number:\s*(.+)",
        "poNumber": r"PO Number:\s*(.+)",
        "totalDue": r"Total Due:\s*(.+)",
        "paymentTerms": r"Payment Terms:\s*(.+)",
        "dueDate": r"Due Date:\s*(.+)",
        "issueDate": r"(?:Invoice Date|PO Date):\s*(.+)",
    }
    for field, pattern in patterns.items():
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            fields[field] = match.group(1).strip()

    # Extract line items from markdown table
    table_rows = re.findall(
        r"\|\s*\d+\s*\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|",
        content,
    )
    if table_rows:
        fields["lineItems"] = [
            {
                "item": row[0].strip(),
                "description": row[1].strip(),
                "qty": row[2].strip(),
                "unitPrice": row[3].strip(),
                "lineTotal": row[4].strip(),
            }
            for row in table_rows
        ]

    return fields


async def _parse_with_document_intelligence(
    doc_id: str,
    endpoint: str,
    azure_client_id: str,
) -> str:
    """Parse a document using Azure Document Intelligence (prebuilt-invoice model)."""
    try:
        from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
        from azure.identity.aio import DefaultAzureCredential

        credential = DefaultAzureCredential(managed_identity_client_id=azure_client_id or None)
        async with DocumentIntelligenceClient(endpoint, credential):
            # In production, doc_id would resolve to a Blob URL
            # For the microhack, we log a clear message
            logger.info("Document Intelligence would parse doc: %s", doc_id)
            return (
                f"Azure Document Intelligence ready to parse {doc_id!r}. "
                "In production, provide a blob storage URL for the document."
            )
    except ImportError:
        return "Azure Document Intelligence SDK not installed."
    except Exception as exc:
        logger.exception("Document Intelligence error for %s", doc_id)
        return f"Document Intelligence error: {exc}"
