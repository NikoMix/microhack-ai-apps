# Module B mapping — labs → controls → evidence

This microhack is engineered so that **doing the labs produces the evidence** required by the
*AI Applications on Microsoft Azure* Advanced Specialization (**Module B**, controls B.1.1–B.4.2).
Control definitions live in [NikoMix/specialization-ai-apps](https://github.com/NikoMix/specialization-ai-apps).

## Control coverage

| Control | What the auditor checks | How this microhack delivers it | Evidence artifact produced |
|---|---|---|---|
| **B.1.1 Azure AI Implementation** | Demonstrated technical capability delivering AI on Azure | Labs 1–6 build a real multi-agent AI app on Azure AI Foundry/OpenAI/Search/Doc Intelligence | Case study, architecture diagram, capability statement, sample deliverables → `docs/evidence-templates/` |
| **B.2.1 ACR Performance** | $15k ACR per pillar across AI, App Platform, Data | The solution consumes services in **all three pillars** (see [architecture](architecture.md)); ACR worksheet shows the mapping | ACR pillar worksheet + Partner Center export walkthrough |
| **B.2.2 Customer Diversity** | ≥3 unique customers via DPOR/PAL/CSP | Three Zava business units modelled as customers; association-types lesson | Customer-diversity table template |
| **B.3.1 Certifications** | 5 individuals across AZ-204, AZ-400, AI-102, DP-420 | Each lab is tagged to exam objectives; the [cert crosswalk](cert-crosswalk.md) maps labs→exams | Cert mapping table + study plan |
| **B.4.1 Audit Readiness** | Structured, organised evidence package | The `trust` agent + capstone assemble a packaged, indexed evidence folder | Evidence index + pre-audit checklist |
| **B.4.2 Partner Onboarding** | Onboarding & delivery templates | Lab outputs are generalised into reusable onboarding/delivery templates | Onboarding pack + delivery templates |

## Lab → control matrix

| Lab | B.1.1 | B.2.1 | B.2.2 | B.3.1 | B.4.1 | B.4.2 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| 0 Setup | | | | ● | | |
| 1 First agent | ● | | | ● | | |
| 2 RAG | ● | ● | | ● | | |
| 3 Deploy to Azure | ● | ● | | ● | | ● |
| 4 Data agents | ● | ● | ● | ● | | |
| 5 Trust & observability | ● | | | ● | ● | |
| 6 Capstone + evidence | ● | ● | ● | ● | ● | ● |

## How "evidence-as-you-go" works

1. Each lab ends with an **"Evidence checkpoint"** that names the artifact(s) it produced and where
   they map.
2. The **Trust & Compliance agent** has a `generate_evidence` tool that compiles those artifacts into
   the Module B folder structure (per control B.4.1) with an Evidence Index.
3. The capstone (Lab 6) runs `generate_evidence` end-to-end so learners leave with a **starter
   evidence package** they can adapt for a real audit.

!!! note "Pre-qualification vs. capability"
    Controls **B.2.1/B.2.2/B.3.1** are *organisational* pre-qualification facts (revenue, customers,
    certified staff) that a classroom cannot literally generate. This microhack teaches **how to
    produce and organise the evidence** for them and **builds the technical capability (B.1.1)** that
    underpins the whole specialization.
