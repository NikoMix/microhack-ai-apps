# B.2.1 — ACR Performance: Pillar Worksheet

> **Control:** B.2.1 ACR (Azure Consumed Revenue) Performance
> **What auditors check:** $15,000 ACR threshold per specialization pillar across AI Services,
> App Platform, and Data — demonstrated through Partner Center export.
> **Evidence required:** ACR pillar worksheet mapping your solution to each pillar, plus a
> Partner Center export walkthrough.

---

## Background — the three specialization pillars

The _AI Applications on Microsoft Azure_ Advanced Specialization requires a partner to show
**$15,000 ACR per qualifying pillar** per trailing 12 months. The three qualifying pillars are:

| Pillar | Qualifying Azure services |
|--------|--------------------------|
| **AI Services** | Azure AI (Foundry, OpenAI, Search, Document Intelligence, Content Safety, Bot Service, etc.) |
| **App Platform** | Azure Container Apps, App Service, Functions, Container Registry, API Management, GitHub, etc. |
| **Data** | Azure Cosmos DB, Azure SQL, Azure Database for PostgreSQL/MySQL, Azure Storage, Synapse, Fabric, etc. |

> **Important:** Each customer engagement may count toward one or more pillars depending on the
> services consumed. The platform you built in this microhack spans **all three pillars**.

---

## Part 1 — Zava Platform ACR Mapping

Use this table to map each deployed service to its qualifying pillar and estimate monthly ACR:

| Service | Resource name | Pillar | Est. monthly ACR (USD) |
|---------|--------------|--------|----------------------:|
| Azure AI Foundry | ai-zava-dev | AI Services | `[PLACEHOLDER]` |
| Azure OpenAI (gpt-4o-mini) | oai-zava-dev | AI Services | `[PLACEHOLDER]` |
| Azure OpenAI (text-embedding-3-small) | oai-zava-dev | AI Services | `[PLACEHOLDER]` |
| Azure AI Search | srch-zava-dev | AI Services | `[PLACEHOLDER]` |
| Azure Document Intelligence | di-zava-dev | AI Services | `[PLACEHOLDER]` |
| Azure AI Content Safety | cs-zava-dev | AI Services | `[PLACEHOLDER]` |
| **AI Services subtotal** | | | **`[PLACEHOLDER]`** |
| Azure Container Apps (3 services) | cae-zava-dev | App Platform | `[PLACEHOLDER]` |
| Azure Container Registry | crzavadev | App Platform | `[PLACEHOLDER]` |
| Azure API Management | apim-zava-dev | App Platform | `[PLACEHOLDER]` |
| **App Platform subtotal** | | | **`[PLACEHOLDER]`** |
| Azure Cosmos DB | cosmos-zava-dev | Data | `[PLACEHOLDER]` |
| Azure Database for PostgreSQL | pg-zava-dev | Data | `[PLACEHOLDER]` |
| **Data subtotal** | | | **`[PLACEHOLDER]`** |
| **Grand total** | | | **`[PLACEHOLDER]`** |

### Pillar qualification summary

| Pillar | Monthly ACR | Meets $15k/yr threshold? |
|--------|------------:|:------------------------:|
| AI Services | `[PLACEHOLDER]` | `[PLACEHOLDER: Yes / No]` |
| App Platform | `[PLACEHOLDER]` | `[PLACEHOLDER: Yes / No]` |
| Data | `[PLACEHOLDER]` | `[PLACEHOLDER: Yes / No]` |

> **Note for the classroom:** The Zava platform as built in the microhack is a _demo scale_
> deployment. A real partner submission needs real customer ACR aggregated across their delivery
> portfolio, not a single lab deployment. The purpose here is to demonstrate **which services
> map to which pillar** so you can match them to your Partner Center data.

---

## Part 2 — Getting ACR data from Partner Center

Follow these steps to export your ACR data for the audit submission.

### Step 1 — Log in to Partner Center

1. Navigate to [Partner Center](https://partner.microsoft.com).
2. Sign in with your organisation's Microsoft Partner Network (MPN) account.

### Step 2 — Go to Insights > Revenue

1. In the left navigation, click **Insights**.
2. Click **Revenue** (or **Azure Consumed Revenue**).
3. Set the date range to the **trailing 12 months**.

### Step 3 — Filter by product family

1. Click the **Product family** filter.
2. Select the services that map to each pillar:
   - **AI Services:** `Cognitive Services`, `Machine Learning`, `Bot Service`
   - **App Platform:** `Container Instances`, `Container Apps`, `App Service`, `Functions`
   - **Data:** `Cosmos DB`, `SQL Database`, `PostgreSQL`, `Storage`

### Step 4 — Export the report

1. Click **Export** → **CSV** or **Excel**.
2. Save as `partner-center-acr-export-YYYYMMDD.xlsx`.

### Step 5 — Map to pillar worksheet

Use the exported data to fill in **Part 1** above. Sum the ACR for each service and enter it in
the pillar subtotal row.

### Partner Center export — what auditors look for

```text
File: partner-center-acr-export-20250701.xlsx
Columns: Subscription ID | Customer | Service | ACR (USD) | Month
Filter: Trailing 12 months | [Partner MPN ID]

Sample rows:
SUB-001 | Zava Retail Stores    | Azure OpenAI          | 1,250.00 | 2025-06
SUB-002 | Zava eCommerce        | Azure AI Search       |   875.00 | 2025-06
SUB-003 | Zava Wholesale        | Azure Cosmos DB       | 2,100.00 | 2025-06
```

> `[PLACEHOLDER: Attach your actual Partner Center export here as a PDF/Excel file.]`

---

## Part 3 — $15k-per-pillar Compliance Notes

!!! note "What counts toward the $15k threshold?"
    - ACR must come from **qualifying Azure services** in each pillar.
    - It can be aggregated across **multiple customers and subscriptions**.
    - The trailing 12-month window is a rolling period — check your Partner Center dashboard for
      the exact dates.
    - Internal/demo subscriptions (like the microhack lab) typically do **not** count toward
      the threshold. Use real customer delivery ACR.

!!! tip "Maximising pillar coverage"
    - **AI Services:** adding Azure Bot Service, Azure Language Service, or Azure Video Indexer
      to customer projects adds qualifying ACR to this pillar.
    - **App Platform:** GitHub Advanced Security subscriptions, Azure DevOps, and Azure Static
      Web Apps qualify.
    - **Data:** Azure Synapse Analytics, Microsoft Fabric, and Azure Databricks qualify for the
      Data pillar.

---

## Part 4 — Evidence attachment checklist

- [ ] `partner-center-acr-export-YYYYMMDD.xlsx` attached
- [ ] Pillar worksheet filled with real ACR values
- [ ] All three pillars meet or exceed $15,000 annual ACR
- [ ] `evidence/b21-resource-inventory-lab3.txt` (service inventory from Lab 3)
- [ ] `evidence/b21-pgvector-seed-lab2.txt` (Data pillar — pgvector 1536-dim)
- [ ] `evidence/b21-cosmos-trace-lab4.png` (Data pillar — Cosmos DB trace)

---

> **Next:** Complete [B.2.2 Customer Diversity Table](b22-customer-diversity.md)
