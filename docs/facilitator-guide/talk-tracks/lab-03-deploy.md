# Talk Track — Lab 3: Deploy to Azure

**Block:** Azure Platform (12:45–13:05) + Lab 3 (13:05–14:00)
**Slides:** Section 6 of `slides/zava-microhack-deck.md`
**Lab guide:** `docs/labs/lab-03-deploy.md`
**Duration:** 20 min lecture + 55 min lab

---

## Azure Platform Lecture (12:45–13:05, 20 min)

### `azd up` in 2 minutes (3 min)

Start with the punchline:

```bash
azd up
# → provisions 15+ Azure resources
# → builds container images + pushes to ACR
# → deploys to Container Apps
# → emits all AZURE_* env vars
```

> "One command. Five minutes. A production-pattern platform on Azure. No ARM JSON.
> No clicking in the portal. Reproducible, auditable, IaC-driven."

### What gets provisioned (5 min)

Walk through the "What Gets Provisioned" slide. Point to each resource and explain:

- **Container Apps Environment** — the hosting fabric for the three services
- **Azure Container Registry (ACR)** — stores the container images; no anonymous pull
- **Azure AI Foundry** — hub + project, deploys `gpt-4o-mini` and `text-embedding-3-small`
- **Azure AI Search** — the `zava-knowledge` index
- **Document Intelligence** — used by Operations agent to parse supplier docs
- **Content Safety** — used by Trust agent to screen replies
- **Cosmos DB** — `products`, `orders`, `customers` containers; key auth disabled
- **PostgreSQL Flexible Server** — `zava` database with pgvector; AAD auth only
- **Key Vault** — all secrets; purge protection on
- **Log Analytics + Application Insights** — observability; receives OTLP traces

### Managed Identity: no keys, ever (5 min)

This is a critical teaching point for the Advanced Specialization and B.4.1:

> "In this platform, there are **no connection strings in the code**. No Cosmos DB keys.
> No API keys. Not even in a `.env` file in production. The Container Apps run as a
> user-assigned Managed Identity. `DefaultAzureCredential` automatically picks up that
> identity and gets a token from Entra ID. The identity has the minimum required RBAC roles
> on each service."

Draw the flow on a whiteboard:

```text
Container App → DefaultAzureCredential → User-assigned Managed Identity
                                         → RBAC role on Cosmos DB
                                         → RBAC role on AI Foundry
                                         → RBAC role on Key Vault
                                         → RBAC role on AI Search
```

> "This is why `disableLocalAuth: true` on Cosmos DB and `anonymousPullEnabled: false`
> on ACR are in the Bicep templates. If a key doesn't exist, a key can't be leaked."

### Bicep + Azure Verified Modules (5 min)

Show the Bicep snippet from the slides:

```bicep
module cosmosAccount 'br/public:avm/res/document-db/database-account:0.8.1' = {
  params: {
    disableLocalAuth: true
    sqlRoleAssignmentsPrincipalIds: [managedIdentity.outputs.principalId]
  }
}
```

Key points:

1. **Azure Verified Modules (AVM)** — Microsoft-maintained, opinionated, secure-by-default Bicep modules
2. The module reference (`br/public:avm/...`) pins to a specific version — reproducible
3. `disableLocalAuth: true` enforces Managed Identity auth for Cosmos DB
4. The `managedIdentity.outputs.principalId` wires the identity to the service automatically

> "This is infrastructure as code that satisfies security best practices out of the box.
> When an auditor asks 'how do you ensure no keys are stored?', you show them this file."

### Introduce Lab 3 (2 min)

> "In the next 55 minutes, you'll run `azd up` and have the complete Zava platform
> running in Azure. You'll verify traces in Application Insights and call the live
> endpoint. If you don't have an Azure subscription, pair with someone who does — or
> observe my deployment on the projector."

---

## Lab 3 (13:05–14:00, 55 min)

### Expected lab flow

1. Attendees run `azd auth login` and `azd up`
2. `azd up` takes ~10–15 minutes — while waiting, they explore the Bicep templates
3. They call the deployed `/health` endpoint to confirm it's running
4. They call `/chat` with a question and check the `traceId` in Application Insights
5. They explore the Managed Identity role assignments in the portal

### While `azd up` is running (10 min buffer activity)

Have attendees:

- Browse `infra/main.bicep` and find the Cosmos DB module — see `disableLocalAuth: true`
- Find the Container Apps definition and spot the `managedIdentityResourceId` wiring
- Look at `azure.yaml` to see the three services (`api-python`, `api-dotnet`, `mcp-zava`)

### Demo cue — trace in Application Insights

After `azd up` completes:

1. Call `/chat` from the terminal
2. Copy the `traceId` from the response
3. Go to Application Insights → Transaction Search → paste the `traceId`
4. Show the end-to-end trace: API receive → Orchestrator → Concierge → tool calls → response

> "This is B.4.1 evidence. An auditor can trace any response to its full execution path —
> what agent handled it, what tools were called, what was retrieved, how long it took."

### Watch for

- **`azd up` quota errors** — common if subscription has low GPU/core quotas.
  Solution: use `eastus` region which typically has more capacity.
- **Image build failures** — usually a `Dockerfile` path issue. Check that Docker is in the PATH.
- **Content Safety not available in region** — Content Safety has limited regional availability.
  Check the build contract for supported regions.
- **Cosmos DB forbidden** — Managed Identity RBAC assignment may not have propagated yet.
  Wait 2–3 minutes and retry.

### Evidence checkpoint

> "After `azd up` succeeds: screenshot the Container Apps in the portal — that's your
> B.2.1 App Platform evidence. Screenshot the Application Insights trace — that's your
> B.4.1 observability evidence. And note the Azure AI Foundry project URL — that's
> your B.1.1 architecture evidence."

---

## Common questions during Lab 3

**Q: Why Container Apps and not App Service or AKS?**

> "Container Apps is the right choice for microservices that scale to zero and don't need
> Kubernetes complexity. It gives us managed ingress, HTTPS, scale rules, and KEDA-based
> scaling — all without managing a cluster. The Advanced Specialization's App Platform
> pillar covers Container Apps, so it also satisfies B.2.1."

**Q: How much will this cost?**

> "For a 1-day workshop, expect less than $5 in Azure consumption. Container Apps bills
> by request and CPU/memory seconds. AI Foundry bills by tokens — with `gpt-4o-mini`,
> a day of lab use is a few cents. The biggest cost is usually the PostgreSQL Flexible
> Server — consider 'Burstable, B1ms' tier for workshops."

**Q: Can I destroy the resources after the lab?**

> "Yes. Run `azd down` to tear everything down cleanly. It will prompt you to confirm
> resource deletion including the Key Vault (which has purge protection — you'll need
> to confirm purge separately)."

**Q: What is `azure.yaml` for?**

> "`azure.yaml` is the azd project configuration. It maps each service name to a source
> directory and a host type (`containerapp`). `azd` uses it to build images, push to ACR,
> and deploy to the right Container App. It's the glue between your code and the infra."
