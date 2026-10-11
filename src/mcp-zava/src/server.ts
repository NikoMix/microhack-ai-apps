/**
 * Zava MCP Server — tool definitions.
 *
 * Each tool maps 1:1 to an agent capability defined in `.microhack/build-contract.md §2`.
 *
 * Tools exposed:
 *   get_product       → concierge / merchandiser
 *   search_products   → merchandiser
 *   get_order         → concierge
 *   get_inventory     → operations
 *   get_customers     → operations / trust
 *   search_knowledge  → concierge RAG over policies + supplier docs
 *   generate_evidence → trust agent (Module B audit evidence)
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { loadData } from "./data/loader.js";
import type { KnowledgeDoc, Product } from "./data/loader.js";

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Return a plain-text JSON block as the tool result content. */
function jsonContent(value: unknown) {
    return { content: [{ type: "text" as const, text: JSON.stringify(value, null, 2) }] };
}

/** Return an error tool result. */
function errorContent(message: string) {
    return {
        content: [{ type: "text" as const, text: message }],
        isError: true,
    };
}

/**
 * Simple keyword search over a document's content.
 * Returns the N lines around each match as an excerpt.
 */
function excerptMatches(doc: KnowledgeDoc, query: string, windowLines = 5): string | null {
    const lc = doc.content.toLowerCase();
    const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.some((t) => lc.includes(t))) return null;

    const lines = doc.content.split("\n");
    const matchedIdx = new Set<number>();

    for (let i = 0; i < lines.length; i++) {
        const ll = (lines[i] ?? "").toLowerCase();
        if (terms.some((t) => ll.includes(t))) {
            for (let j = Math.max(0, i - windowLines); j <= Math.min(lines.length - 1, i + windowLines); j++) {
                matchedIdx.add(j);
            }
        }
    }
    if (matchedIdx.size === 0) return null;

    return [...matchedIdx]
        .sort((a, b) => a - b)
        .map((i) => lines[i])
        .join("\n");
}

// ── Server factory ────────────────────────────────────────────────────────────

/**
 * Creates and configures the Zava MCP server with all tools registered.
 * Called once at startup.
 */
export async function createZavaServer(): Promise<McpServer> {
    const data = loadData();

    const server = new McpServer({
        name: "zava-mcp-server",
        version: "1.0.0",
    });

    // ── Tool: get_product ─────────────────────────────────────────────────────

    server.tool(
        "get_product",
        "Retrieve a single Zava product by its ID (e.g. ZAVA-RUN-001). " +
        "Returns full product details including price, sizes, colors, smart features, and stock.",
        {
            productId: z
                .string()
                .describe("Stable product ID, e.g. ZAVA-RUN-001 or ZAVA-JKT-003"),
        },
        async ({ productId }) => {
            const product = data.products.find((p) => p.id === productId);
            if (!product) {
                return errorContent(
                    `Product '${productId}' not found. ` +
                    `Available IDs: ${data.products.map((p) => p.id).join(", ")}`
                );
            }
            return jsonContent(product);
        }
    );

    // ── Tool: search_products ─────────────────────────────────────────────────

    server.tool(
        "search_products",
        "Search Zava products by a text query and/or category filter. " +
        "Searches product name, description, smart features, and subcategory. " +
        "Categories: Tops, Bottoms, Outerwear, Accessories, Footwear.",
        {
            query: z
                .string()
                .optional()
                .describe("Free-text search — matched against name, description, smart features"),
            category: z
                .string()
                .optional()
                .describe("Exact category filter, e.g. 'Tops' or 'Footwear'"),
            limit: z
                .number()
                .int()
                .min(1)
                .max(50)
                .default(10)
                .describe("Maximum number of results (default 10, max 50)"),
        },
        async ({ query, category, limit }) => {
            let results: Product[] = [...data.products];

            if (category) {
                results = results.filter(
                    (p) => p.category.toLowerCase() === category.toLowerCase()
                );
            }

            if (query) {
                const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
                results = results.filter((p) => {
                    const haystack = [
                        p.name,
                        p.description,
                        p.subcategory,
                        ...p.smartFeatures,
                    ]
                        .join(" ")
                        .toLowerCase();
                    return terms.every((t) => haystack.includes(t));
                });
            }

            // Sort by rating (highest first) then alphabetically
            results.sort((a, b) => b.rating - a.rating || a.name.localeCompare(b.name));
            results = results.slice(0, limit);

            return jsonContent({
                count: results.length,
                products: results.map((p) => ({
                    id: p.id,
                    name: p.name,
                    category: p.category,
                    price: p.price,
                    rating: p.rating,
                    inStock: p.inStock,
                    description: p.description.slice(0, 120),
                })),
            });
        }
    );

    // ── Tool: get_order ───────────────────────────────────────────────────────

    server.tool(
        "get_order",
        "Retrieve a Zava order by its ID (e.g. ZO-100431). " +
        "Returns order details including status, line items, total, and shipping address.",
        {
            orderId: z
                .string()
                .describe("Order ID in ZO-XXXXXX format, e.g. ZO-100431"),
        },
        async ({ orderId }) => {
            const order = data.orders.find((o) => o.orderId === orderId);
            if (!order) {
                return errorContent(
                    `Order '${orderId}' not found. ` +
                    `Available IDs: ${data.orders.map((o) => o.orderId).join(", ")}`
                );
            }
            return jsonContent(order);
        }
    );

    // ── Tool: get_inventory ───────────────────────────────────────────────────

    server.tool(
        "get_inventory",
        "Get current inventory (in-stock quantity) for one or all Zava products. " +
        "Omit productId to retrieve the full inventory snapshot.",
        {
            productId: z
                .string()
                .optional()
                .describe("Product ID to check; omit to return all inventory levels"),
            lowStockThreshold: z
                .number()
                .int()
                .min(0)
                .default(100)
                .describe("Flag products at or below this quantity as low-stock (default 100)"),
        },
        async ({ productId, lowStockThreshold }) => {
            const products = productId
                ? data.products.filter((p) => p.id === productId)
                : data.products;

            if (productId && products.length === 0) {
                return errorContent(`Product '${productId}' not found.`);
            }

            const inventory = products.map((p) => ({
                productId: p.id,
                name: p.name,
                category: p.category,
                inStock: p.inStock,
                status: p.inStock === 0 ? "out-of-stock" : p.inStock <= lowStockThreshold ? "low-stock" : "in-stock",
            }));

            const summary = {
                total: products.length,
                outOfStock: inventory.filter((i) => i.status === "out-of-stock").length,
                lowStock: inventory.filter((i) => i.status === "low-stock").length,
                inStock: inventory.filter((i) => i.status === "in-stock").length,
            };

            return jsonContent({ summary, inventory });
        }
    );

    // ── Tool: get_customers ───────────────────────────────────────────────────

    server.tool(
        "get_customers",
        "Retrieve Zava business unit (customer) records. " +
        "These are the three Zava internal customers used for Module B control B.2.2 " +
        "(customer diversity): Zava Retail Stores, Zava eCommerce, Zava Wholesale.",
        {
            customerId: z
                .string()
                .optional()
                .describe(
                    "Customer ID, e.g. ZAVA-BU-RETAIL, ZAVA-BU-ECOM, ZAVA-BU-WHOLESALE; " +
                    "omit to return all"
                ),
        },
        async ({ customerId }) => {
            if (customerId) {
                const customer = data.customers.find((c) => c.id === customerId);
                if (!customer) {
                    return errorContent(
                        `Customer '${customerId}' not found. ` +
                        `Valid IDs: ${data.customers.map((c) => c.id).join(", ")}`
                    );
                }
                return jsonContent(customer);
            }
            return jsonContent({ count: data.customers.length, customers: data.customers });
        }
    );

    // ── Tool: search_knowledge ────────────────────────────────────────────────

    server.tool(
        "search_knowledge",
        "Search the Zava knowledge base — returns relevant excerpts from policy and supplier " +
        "documents. Used by the Concierge agent for RAG-style grounding and by the " +
        "Operations agent for supplier document parsing.",
        {
            query: z
                .string()
                .min(2)
                .describe("Search terms, e.g. 'returns smart garment 45 days'"),
            source: z
                .enum(["all", "policies", "suppliers"])
                .default("all")
                .describe("Limit search to a specific document source (default: all)"),
            limit: z
                .number()
                .int()
                .min(1)
                .max(10)
                .default(3)
                .describe("Maximum number of document excerpts to return (default 3)"),
        },
        async ({ query, source, limit }) => {
            const docs = source === "all"
                ? data.knowledge
                : data.knowledge.filter((d) => d.source === source);

            const results: Array<{
                source: string;
                slug: string;
                excerpt: string;
            }> = [];

            for (const doc of docs) {
                if (results.length >= limit) break;
                const excerpt = excerptMatches(doc, query);
                if (excerpt) {
                    results.push({ source: doc.source, slug: doc.slug, excerpt });
                }
            }

            if (results.length === 0) {
                return jsonContent({
                    found: 0,
                    message: `No documents matched '${query}' in source '${source}'.`,
                    results: [],
                });
            }

            return jsonContent({ found: results.length, results });
        }
    );

    // ── Tool: generate_evidence ───────────────────────────────────────────────

    server.tool(
        "generate_evidence",
        "Assemble a Module B evidence skeleton for the AI Applications on Microsoft Azure " +
        "Advanced Specialization. Produces a structured Markdown document covering controls " +
        "B.1.1–B.4.2. Used by the Trust & Compliance agent (Lab 6 capstone).",
        {
            partnerName: z
                .string()
                .default("Zava (Demo Partner)")
                .describe("Partner company name to include in the evidence document"),
            controls: z
                .array(z.enum(["B.1.1", "B.2.1", "B.2.2", "B.3.1", "B.4.1", "B.4.2"]))
                .default(["B.1.1", "B.2.1", "B.2.2", "B.3.1", "B.4.1", "B.4.2"])
                .describe("List of Module B controls to include (default: all)"),
            solutionTitle: z
                .string()
                .default("Zava AI Agent Platform")
                .describe("Title of the delivered AI solution"),
            labsCompleted: z
                .array(z.string())
                .default(["Lab 1", "Lab 2", "Lab 3", "Lab 4", "Lab 5", "Lab 6"])
                .describe("List of lab names completed to include in the crosswalk"),
        },
        async ({ partnerName, controls, solutionTitle, labsCompleted }) => {
            const now = new Date().toISOString().split("T")[0] ?? new Date().toISOString();

            const controlDefs: Record<string, { title: string; auditorCheck: string; delivered: string }> = {
                "B.1.1": {
                    title: "Azure AI Implementation",
                    auditorCheck: "Demonstrated technical capability delivering AI on Azure",
                    delivered:
                        `Built a production-grade multi-agent AI application (${solutionTitle}) on ` +
                        "Azure AI Foundry, Azure OpenAI, Azure AI Search, and Azure Container Apps. " +
                        "Source code in this repository evidences the capability.",
                },
                "B.2.1": {
                    title: "ACR Performance",
                    auditorCheck: "$15k ACR per pillar across AI, App Platform, Data",
                    delivered:
                        "Solution spans all three Advanced Specialization ACR pillars: " +
                        "AI Services (Azure AI Foundry, OpenAI, Search, Document Intelligence, Content Safety), " +
                        "App Platform (Container Apps, ACR, API Management), " +
                        "Data (Cosmos DB, PostgreSQL Flexible + pgvector).",
                },
                "B.2.2": {
                    title: "Customer Diversity",
                    auditorCheck: "≥3 unique customers via DPOR / PAL / CSP",
                    delivered:
                        `Three ${partnerName} business units modelled as customers: ` +
                        "Zava eCommerce (DPOR), Zava Retail Stores (PAL), Zava Wholesale (CSP). " +
                        "See data/customers.json for the association-type mapping.",
                },
                "B.3.1": {
                    title: "Certifications",
                    auditorCheck: "5 individuals across AZ-204, AZ-400, AI-102, DP-420",
                    delivered:
                        `Labs completed: ${labsCompleted.join(", ")}. ` +
                        "Each lab maps to AZ-204, AI-102, DP-420, and/or AZ-400 objectives " +
                        "per docs/module-b-mapping.md and docs/cert-crosswalk.md.",
                },
                "B.4.1": {
                    title: "Audit Readiness",
                    auditorCheck: "Structured, organised evidence package",
                    delivered:
                        "This generated evidence document, combined with architecture diagrams " +
                        "in docs/architecture.md, lab outputs, and the pre-audit checklist in " +
                        "docs/evidence-templates/, forms the complete audit package.",
                },
                "B.4.2": {
                    title: "Partner Onboarding",
                    auditorCheck: "Onboarding & delivery templates",
                    delivered:
                        "Lab outputs (architecture diagrams, capability statements, runbooks) " +
                        "have been generalised into reusable onboarding and delivery templates " +
                        "in docs/evidence-templates/.",
                },
            };

            const customerSummary = data.customers
                .map((c) => `| ${c.name} | ${c.associationType} | ${c.primaryPillars.join(", ")} |`)
                .join("\n");

            const productCount = data.products.length;
            const orderCount = data.orders.length;

            const sections = controls.map((ctrl) => {
                const def = controlDefs[ctrl];
                if (!def) return "";
                return [
                    `## ${ctrl} — ${def.title}`,
                    "",
                    `**Auditor check:** ${def.auditorCheck}`,
                    "",
                    `**How ${partnerName} delivers it:** ${def.delivered}`,
                    "",
                    "**Evidence artefacts:**",
                    "- Source code: `src/python/` and `src/dotnet/`",
                    "- Infrastructure: `infra/` (Bicep AVM, deployed with azd)",
                    "- Architecture: `docs/architecture.md`",
                    "- Lab guides: `docs/labs/`",
                    "- This document (generated by `trust` agent, `generate_evidence` tool)",
                    "",
                ].join("\n");
            });

            const doc = [
                `# Module B Evidence Package`,
                ``,
                `**Partner:** ${partnerName}`,
                `**Solution:** ${solutionTitle}`,
                `**Generated:** ${now}`,
                `**Labs completed:** ${labsCompleted.join(", ")}`,
                ``,
                `> This document was assembled automatically by the Zava \`trust\` agent using`,
                `> the \`generate_evidence\` MCP tool. Use it as a **starter template** — `,
                `> review each section and add partner-specific supporting evidence before`,
                `> submitting to the Advanced Specialization audit team.`,
                ``,
                `---`,
                ``,
                `## Customer Diversity (B.2.2 snapshot)`,
                ``,
                `| Customer | Association Type | Primary Pillars |`,
                `|---|---|---|`,
                customerSummary,
                ``,
                `---`,
                ``,
                `## Azure Services Deployed`,
                ``,
                `| Pillar | Services |`,
                `|---|---|`,
                `| AI Services | Azure AI Foundry, Azure OpenAI (gpt-4o-mini + text-embedding-3-small), Azure AI Search, Document Intelligence, Content Safety |`,
                `| App Platform | Azure Container Apps, Azure Container Registry, API Management |`,
                `| Data | Azure Cosmos DB (\`${productCount}\` product SKUs, \`${orderCount}\` sample orders), PostgreSQL Flexible Server (pgvector) |`,
                ``,
                `---`,
                ``,
                ...sections,
                `---`,
                ``,
                `## Pre-Audit Checklist`,
                ``,
                `- [ ] Architecture diagram reviewed and exported (see \`docs/architecture.md\`)`,
                `- [ ] All lab outputs committed and tagged in git`,
                `- [ ] Certified staff roster confirmed (AZ-204, AI-102, DP-420, AZ-400)`,
                `- [ ] Customer association evidence uploaded to Partner Center`,
                `- [ ] ACR pillar worksheet completed`,
                `- [ ] Evidence package index created in \`docs/evidence-templates/\``,
                ``,
            ].join("\n");

            return { content: [{ type: "text" as const, text: doc }] };
        }
    );

    return server;
}
