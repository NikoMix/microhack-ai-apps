# B.2.2 — Customer Diversity Table

> **Control:** B.2.2 Customer Diversity
> **What auditors check:** ≥3 unique customers consuming Azure services via DPOR, PAL, or CSP
> association. Customers must be independent organisations (not subsidiaries of one another).
> **Evidence required:** Customer diversity table, association type documentation.

---

## Background — association types

Microsoft tracks partner-customer relationships through three mechanisms:

| Association type | What it is | When to use |
|-----------------|-----------|------------|
| **DPOR** (Digital Partner of Record) | Partner is linked to a specific Azure subscription as the primary influencer | Project-based engagements where you managed or implemented the solution |
| **PAL** (Partner Admin Link) | Partner's Entra ID (Azure AD) object is linked to the customer's subscription | Managed services, ongoing support, or co-delivery engagements |
| **CSP** (Cloud Solution Provider) | Partner provisions and invoices Azure services to the customer | You are the customer's Azure reseller |

!!! tip "Which to use?"
    - **Greenfield implementations:** use PAL — it's the easiest to set up.
    - **Reseller engagements:** use CSP.
    - **Legacy project links:** check if DPOR is already in place.
    - You may have multiple association types with the same customer (PAL + CSP is common).

---

## Part 1 — Customer Diversity Table

> Fill in three or more real customers. The Zava business units below are **examples only** —
> use real customer names for the actual submission.

### Microhack training example (Zava business units)

| # | Customer name | Industry | Azure subscription ID | Association type | Primary pillar consumed | ACR (trailing 12 mo) |
|---|--------------|----------|----------------------|-----------------|------------------------|---------------------:|
| 1 | Zava Retail Stores | Retail | `[PLACEHOLDER: Sub ID]` | PAL / DPOR | AI Services + App Platform | `[PLACEHOLDER]` |
| 2 | Zava eCommerce | Retail / eCommerce | `[PLACEHOLDER: Sub ID]` | PAL | AI Services + Data | `[PLACEHOLDER]` |
| 3 | Zava Wholesale | B2B Wholesale | `[PLACEHOLDER: Sub ID]` | CSP | Data + App Platform | `[PLACEHOLDER]` |

### Your real customer table (for submission)

> Replace the Zava rows with your actual customer engagements.

| # | Customer name | Industry | Azure subscription ID | Association type | Primary pillar | ACR (trailing 12 mo) |
|---|--------------|----------|----------------------|-----------------|---------------|---------------------:|
| 1 | `[PLACEHOLDER: Customer name]` | `[PLACEHOLDER]` | `[PLACEHOLDER]` | `[PLACEHOLDER: DPOR/PAL/CSP]` | `[PLACEHOLDER]` | `[PLACEHOLDER]` |
| 2 | `[PLACEHOLDER: Customer name]` | `[PLACEHOLDER]` | `[PLACEHOLDER]` | `[PLACEHOLDER: DPOR/PAL/CSP]` | `[PLACEHOLDER]` | `[PLACEHOLDER]` |
| 3 | `[PLACEHOLDER: Customer name]` | `[PLACEHOLDER]` | `[PLACEHOLDER]` | `[PLACEHOLDER: DPOR/PAL/CSP]` | `[PLACEHOLDER]` | `[PLACEHOLDER]` |

---

## Part 2 — Establishing PAL associations

To claim ACR via PAL for new customers:

### Step 1 — Get your MPN ID

```text
Partner Center → Account settings → Identifiers → Microsoft AI Cloud Partner Program ID (MPN)
```

### Step 2 — Link from a user account with customer access

```bash
# Authenticate as a user with access to the customer subscription
az login

# Link PAL
az managedservices partner-id update --partner-id <YOUR_MPN_ID>
```

Or via Azure Portal:

1. Log in to [Azure Portal](https://portal.azure.com) as a user with Reader+ access to the
   customer subscription.
2. Search for **Partner ID** in the top search bar.
3. Click **Link a partner account**.
4. Enter your MPN ID and click **Associate**.

### Step 3 — Verify the link

```bash
az managedservices partner-id show
```

```json
{
  "partnerId": "1234567",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

---

## Part 3 — DPOR attachment walkthrough

If you managed the customer's solution and want to claim DPOR:

1. Go to Partner Center → **Customers** → select the customer.
2. Click **Azure subscriptions** → select the target subscription.
3. Click **Add DPOR** and complete the form (project name, dates, solution area).
4. The customer approves via email notification.

---

## Part 4 — CSP customer list

If customers are transacting through CSP, the association is automatic. Export the CSP customer
list from Partner Center:

```text
Partner Center → Customers → Export (CSV)
```

> `[PLACEHOLDER: Attach CSP customer export here, or reference Partner Center report.]`

---

## Part 5 — Zava business-unit data (from the microhack)

The three Zava business units modelled in the lab map directly to the B.2.2 customer diversity
narrative:

```json
[
  {
    "id": "cust-retail",
    "name": "Zava Retail Stores",
    "channel": "Physical stores",
    "use_case": "Store associates: product Q&A, returns, inventory",
    "primary_agents": ["concierge", "operations"]
  },
  {
    "id": "cust-ecommerce",
    "name": "Zava eCommerce",
    "channel": "Web and mobile",
    "use_case": "Personalised recommendations, order tracking",
    "primary_agents": ["concierge", "merchandiser"]
  },
  {
    "id": "cust-wholesale",
    "name": "Zava Wholesale",
    "channel": "B2B — gyms and sports teams",
    "use_case": "Bulk order management, supplier document parsing",
    "primary_agents": ["operations", "merchandiser"]
  }
]
```

The data is in `data/customers.json`. Lab 4 queries each unit separately to produce the
`b22-business-unit-queries-lab4.txt` evidence artifact.

---

## Part 6 — Evidence attachment checklist

- [ ] Customer diversity table filled with ≥ 3 real customers
- [ ] Association type (DPOR/PAL/CSP) documented for each customer
- [ ] Partner Center screenshot showing each customer's subscription linkage
- [ ] `evidence/b22-business-unit-queries-lab4.txt` (from Lab 4)
- [ ] ACR per customer verified in Partner Center export

---

> **Next:** Complete [B.4.1 Evidence Index & Pre-Audit Checklist](b41-evidence-index.md)
