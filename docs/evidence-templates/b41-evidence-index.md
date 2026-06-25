# B.4.1 — Audit Readiness: Evidence Index & Pre-Audit Checklist

> **Control:** B.4.1 Audit Readiness
> **What auditors check:** An organised, complete evidence package covering all Module B controls.
> A partner that can present a structured, indexed evidence folder demonstrates operational
> maturity and substantially reduces audit duration.
> **Evidence required:** Evidence index, pre-audit checklist, artifact bundle.

---

## Part 1 — Evidence Index

> This index is auto-populated by the `trust` agent's `generate_evidence` tool in Lab 6.
> Review and complete each section.

**Package version:** `[PLACEHOLDER: v1.0 | YYYY-MM-DD]`

**Prepared by:** `[PLACEHOLDER: Name, Title]`

**Submission date:** `[PLACEHOLDER: YYYY-MM-DD]`

**Partner organisation:** `[PLACEHOLDER: Company name]`

**MPN ID:** `[PLACEHOLDER: 7-digit MPN ID]`

---

### B.1.1 — Azure AI Implementation

| Artifact | Source | Date | Status |
|----------|--------|------|--------|
| Architecture diagram | `docs/architecture.md` | Lab 3 | ☐ Complete |
| Capability case study | `docs/evidence-templates/b11-capability-case-study.md` | Lab 6 | ☐ Complete |
| Agent transcript (multi-turn) | `evidence/b11-agent-transcript-lab1.txt` | Lab 1 | ☐ Complete |
| RAG citations screenshot | `evidence/b11-rag-citations-lab2.png` | Lab 2 | ☐ Complete |
| Application Insights trace | `evidence/b11-appi-trace-lab3.png` | Lab 3 | ☐ Complete |
| App Insights waterfall | `evidence/b11-appi-waterfall-lab5.png` | Lab 5 | ☐ Complete |
| GitHub repository URL | `[PLACEHOLDER: https://github.com/...]` | — | ☐ Complete |

### B.2.1 — ACR Performance

| Artifact | Source | Date | Status |
|----------|--------|------|--------|
| ACR pillar worksheet | `docs/evidence-templates/b21-acr-pillar-worksheet.md` | Lab 6 | ☐ Complete |
| Partner Center ACR export | `partner-center-acr-export-YYYYMMDD.xlsx` | — | ☐ Complete |
| Resource inventory | `evidence/b21-resource-inventory-lab3.txt` | Lab 3 | ☐ Complete |
| pgvector seed output | `evidence/b21-pgvector-seed-lab2.txt` | Lab 2 | ☐ Complete |
| Cosmos DB trace | `evidence/b21-cosmos-trace-lab4.png` | Lab 4 | ☐ Complete |

### B.2.2 — Customer Diversity

| Artifact | Source | Date | Status |
|----------|--------|------|--------|
| Customer diversity table | `docs/evidence-templates/b22-customer-diversity.md` | Lab 6 | ☐ Complete |
| Business unit query output | `evidence/b22-business-unit-queries-lab4.txt` | Lab 4 | ☐ Complete |
| PAL/DPOR/CSP screenshots | `[PLACEHOLDER: path/to/screenshots]` | — | ☐ Complete |

### B.3.1 — Certifications

| Artifact | Source | Date | Status |
|----------|--------|------|--------|
| Cert crosswalk | `docs/cert-crosswalk.md` | Lab 0 | ☐ Complete |
| 5-person study plan | `docs/cert-crosswalk.md#study-plan` | — | ☐ Complete |
| Certification screenshots × 5 | `[PLACEHOLDER: path/to/certs]` | — | ☐ Complete |

### B.4.1 — Audit Readiness

| Artifact | Source | Date | Status |
|----------|--------|------|--------|
| This evidence index | `docs/evidence-templates/b41-evidence-index.md` | Lab 6 | ☐ Complete |
| Pre-audit checklist | See Part 2 below | Lab 6 | ☐ Complete |
| Latency alert config | Lab 5 (`az monitor metrics alert`) | Lab 5 | ☐ Complete |
| App Insights waterfall | `evidence/b41-appi-waterfall-lab5.png` | Lab 5 | ☐ Complete |

### B.4.2 — Partner Onboarding

| Artifact | Source | Date | Status |
|----------|--------|------|--------|
| Partner onboarding pack | `docs/evidence-templates/b42-onboarding-pack.md` | Lab 6 | ☐ Complete |
| Bicep IaC modules | `infra/` | Lab 3 | ☐ Complete |
| Delivery runbook | `docs/evidence-templates/b42-onboarding-pack.md#runbook` | Lab 6 | ☐ Complete |

---

## Part 2 — Pre-Audit Checklist

Work through this checklist before submitting. Items marked with **★** are most commonly
queried by auditors.

### Technical controls

- [ ] ★ All Azure services authenticated via **Managed Identity** (no API keys in code or config)
- [ ] ★ **Key Vault** deployed with purge protection enabled
- [ ] ★ **Cosmos DB** key-auth disabled (`disableLocalAuth: true`)
- [ ] **ACR** anonymous pull disabled (`anonymousPullEnabled: false`)
- [ ] **OpenTelemetry** traces flow to Application Insights
- [ ] Every `/chat` response carries a non-null `traceId`
- [ ] Content Safety gate blocks unsafe inputs (Lab 5 Step 2 verified)
- [ ] Latency alert configured (Lab 5 Step 5)

### Architecture

- [ ] ★ Architecture diagram matches deployed resource group
- [ ] All three ACR pillars covered by deployed services
- [ ] `azd provision --preview` output saved and matches actual deployment

### Security & compliance

- [ ] No secrets committed to the repository (git history clean)
- [ ] `.env` in `.gitignore`
- [ ] `pip-audit` / `dotnet list package --vulnerable` shows zero known vulnerabilities
- [ ] `ruff` / `markdownlint` pass with zero errors

### Evidence package

- [ ] ★ All six B.1.1–B.4.2 control sections populated in the evidence index
- [ ] ★ Evidence index artifact count ≥ 1 per control
- [ ] Partner Center ACR export attached (trailing 12 months)
- [ ] Customer diversity table has ≥ 3 real customers with association type
- [ ] ★ Cert crosswalk lists ≥ 5 individuals with passing exam dates
- [ ] Evidence bundle archived (`.zip` or `.tar.gz`) and stored securely

### Organisational

- [ ] ★ MPN ID confirmed active in Partner Center
- [ ] Microsoft AI Cloud Partner Program membership current
- [ ] All listed certifications verified against Microsoft Learn transcript
- [ ] Customer case study reviewed and approved by customer (if using real customer)

---

## Part 3 — Audit interview preparation

Auditors typically ask the following questions. Prepare concise answers.

| Question | Evidence to reference |
|---------|----------------------|
| "Walk me through your architecture." | Architecture diagram in B.1.1 case study |
| "How do you handle secrets?" | Key Vault setup; no keys in code |
| "Show me a real AI call." | Agent transcript + traceId in App Insights |
| "Which customers did you deliver this to?" | B.2.2 customer diversity table |
| "How do your certifications map to the solution?" | B.3.1 cert crosswalk |
| "What Azure revenue does this generate?" | B.2.1 ACR worksheet + Partner Center export |

---

## Part 4 — Evidence bundle export

```bash
# Create the evidence bundle
tar -czf module-b-evidence-$(date +%Y%m%d).tar.gz \
    evidence/ \
    docs/evidence-templates/ \
    docs/architecture.md \
    docs/cert-crosswalk.md

# Verify the bundle
tar -tzf module-b-evidence-$(date +%Y%m%d).tar.gz | head -30
```

> `[PLACEHOLDER: Upload bundle to your secure document management system or Partner Center
> evidence library.]`

---

> **Next:** Complete [B.4.2 Partner Onboarding Pack](b42-onboarding-pack.md)
