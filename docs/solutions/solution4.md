# Solution 4 — Data Agents: Merchandiser & Operations

> **Facilitator note:** Students often confuse `merchandiser` (product data) with `operations`
> (inventory/supply chain). The strongest evidence moment is the three distinct business-unit
> queries returning different order sets — make sure students run all three.

## Expected command outputs

### Merchandiser: product search

```json
{
  "reply": "Here are the top smart running products under $200:\n1. ZP-001 Connected Running Shirt — $149.99. Biometric sensors, Bluetooth 5.2.\n2. ZP-004 Smart Training Socks — $49.99. Stride analysis, washable sensors.\n3. ZP-007 Aerodynamic Running Cap — $79.99. UV sensor, smart sweatband.",
  "agent": "merchandiser",
  "citations": [],
  "traceId": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
}
```

### Merchandiser: reviews for ZP-001

```json
{
  "reply": "ZP-001 Connected Running Shirt has an average rating of 4.6/5 (23 reviews). Customers praise the biometric accuracy and comfort. Common themes: excellent Bluetooth connectivity, true-to-size fit. A few note that the charging cable is proprietary.",
  "agent": "merchandiser",
  "citations": [],
  "traceId": "b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5"
}
```

### Operations: inventory check

```json
{
  "reply": "ZP-003 Recovery Leggings currently have 47 units in stock across all sizes. Size breakdown: XS: 8, S: 12, M: 15, L: 9, XL: 3. XL is running low.",
  "agent": "operations",
  "citations": [],
  "traceId": "c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6"
}
```

### Operations: restock suggestion

```json
{
  "reply": "The following products need restocking:\n- ZP-002 Temperature-Adaptive Jacket (XL: 2 units) — suggest reorder 30 units\n- ZP-003 Recovery Leggings (XL: 3 units) — suggest reorder 25 units\n- ZP-009 Smart Compression Sleeves (all sizes: 15 units) — suggest reorder 50 units",
  "agent": "operations",
  "citations": [],
  "traceId": "d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1"
}
```

### Operations: supplier document parsing

```json
{
  "reply": "SUP-001 invoice dated 2025-06-01 contains 3 line items:\n1. ZP-001 Connected Running Shirt × 500 @ $45.00 = $22,500\n2. ZP-003 Recovery Leggings × 300 @ $32.50 = $9,750\n3. ZP-007 Aerodynamic Running Cap × 200 @ $28.00 = $5,600\nTotal: $37,850. Payment due: 2025-06-30.",
  "agent": "operations",
  "citations": [
    {
      "source": "data/suppliers/sup-001-invoice.md",
      "chunk": "LINE ITEM: ZP-001 × 500 @ $45.00",
      "score": 1.0
    }
  ],
  "traceId": "e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
}
```

## Business-unit queries (B.2.2 evidence)

### Zava Retail Stores

```json
{
  "reply": "Zava Retail Stores has 4 active orders: ZO-001 (shipped), ZO-004 (delivered), ZO-007 (processing), ZO-010 (shipped). Total order value: $4,820.",
  "agent": "operations",
  "citations": [],
  "traceId": "f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3"
}
```

### Zava eCommerce

```json
{
  "reply": "Zava eCommerce has 3 active orders: ZO-002 (processing), ZO-005 (shipped), ZO-008 (delivered). Total order value: $2,340.",
  "agent": "operations",
  "citations": [],
  "traceId": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
}
```

### Zava Wholesale

```json
{
  "reply": "Zava Wholesale has 3 active orders: ZO-003 (delivered), ZO-006 (shipped), ZO-009 (processing). Total order value: $18,600 (bulk rates applied).",
  "agent": "operations",
  "citations": [],
  "traceId": "b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5"
}
```

_Note how Wholesale shows significantly higher order values — this reflects B2B pricing in the
seed data and reinforces the three-customer diversity narrative._

## Filled evidence artifacts

### b22-business-unit-queries-lab4.txt

```text
ZAVA CUSTOMER DIVERSITY EVIDENCE — Lab 4
Date: 2025-07-01

Business Unit 1: Zava Retail Stores
  Active orders: 4 (ZO-001, ZO-004, ZO-007, ZO-010)
  Order value: $4,820
  Channel: Physical retail stores + associates

Business Unit 2: Zava eCommerce
  Active orders: 3 (ZO-002, ZO-005, ZO-008)
  Order value: $2,340
  Channel: Web and mobile storefront

Business Unit 3: Zava Wholesale
  Active orders: 3 (ZO-003, ZO-006, ZO-009)
  Order value: $18,600 (bulk)
  Channel: B2B — gyms and sports teams

These three business units map to B.2.2 Customer Diversity requirement:
≥3 unique customers with diverse use cases.
```

## Common failure modes

| Failure | Root cause | Fix |
|---------|-----------|-----|
| `parse_supplier_doc` returns stub | `AZURE_DOCINTEL_ENDPOINT` not set | Set the endpoint; check MI has `Cognitive Services User` role |
| All three BU queries return the same orders | Seed data missing `customerId` field | Re-run `seed.py --target azure` |
| Merchandiser returns generic text | Products not seeded to Cosmos DB | Run `seed.py --target azure` for products |
| `restock_suggestion` shows no items | Inventory levels all normal in seed data | Edit `data/products.json` to lower a stock level for demo |
