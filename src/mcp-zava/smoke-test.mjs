/**
 * Zava MCP Server — smoke test.
 *
 * Builds the server, then connects as an MCP client via STDIO to verify:
 *   1. The server starts without errors.
 *   2. `tools/list` returns all 7 expected tools.
 *   3. `tools/call` for `get_product` returns valid product data.
 *
 * Usage:
 *   npm run smoke-test          # builds first, then runs this test
 *
 * This file is plain JavaScript (ESM) so it runs with `node` without
 * needing tsx or a TypeScript compilation step beyond the server build.
 */
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execSync } from "node:child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const EXPECTED_TOOLS = [
    "get_product",
    "search_products",
    "get_order",
    "get_inventory",
    "get_customers",
    "search_knowledge",
    "generate_evidence",
];

// ── Step 0: Ensure the server is built ────────────────────────────────────────

console.log("🔨 Building Zava MCP Server...");
execSync("npm run build", { stdio: "inherit", cwd: __dirname });
console.log("✅ Build succeeded.\n");

// ── Step 1: Connect to the server via STDIO ───────────────────────────────────

const serverPath = resolve(__dirname, "dist", "index.js");

// DATA_DIR points to the repo-root data/ directory.
const dataDir = resolve(__dirname, "../../data");

const transport = new StdioClientTransport({
    command: "node",
    args: [serverPath],
    env: {
        ...Object.fromEntries(
            Object.entries(process.env).filter(([, v]) => v !== undefined)
        ),
        DATA_DIR: dataDir,
    },
});

const client = new Client(
    { name: "zava-smoke-test", version: "1.0.0" },
    { capabilities: {} }
);

console.log("🔌 Connecting to Zava MCP Server (STDIO)...");
await client.connect(transport);
console.log("✅ Connected.\n");

// ── Step 2: List tools ────────────────────────────────────────────────────────

console.log("📋 Listing tools...");
const { tools } = await client.listTools();

const toolNames = tools.map((t) => t.name);
console.log(`   Found ${tools.length} tool(s):`);
for (const t of tools) {
    const mark = EXPECTED_TOOLS.includes(t.name) ? "✅" : "⚠️ ";
    console.log(`   ${mark} ${t.name}`);
    if (t.description) {
        console.log(`      ${t.description.slice(0, 80)}...`);
    }
}

const missing = EXPECTED_TOOLS.filter((name) => !toolNames.includes(name));
if (missing.length > 0) {
    console.error(`\n❌ Missing expected tools: ${missing.join(", ")}`);
    process.exit(1);
}
console.log(`\n✅ All ${EXPECTED_TOOLS.length} expected tools are registered.\n`);

// ── Step 3: Call get_product ──────────────────────────────────────────────────

console.log("📦 Calling get_product(ZAVA-RUN-001)...");
const productResult = await client.callTool({
    name: "get_product",
    arguments: { productId: "ZAVA-RUN-001" },
});

if (productResult.isError) {
    console.error("❌ get_product returned an error:", productResult.content);
    process.exit(1);
}

const productText = productResult.content[0]?.text ?? "";
const product = JSON.parse(productText);
console.log("   Result:");
console.log(`   • Name:     ${product.name}`);
console.log(`   • Category: ${product.category}`);
console.log(`   • Price:    $${product.price}`);
console.log(`   • Rating:   ${product.rating}`);
console.log(`   • In Stock: ${product.inStock}`);
console.log("✅ get_product succeeded.\n");

// ── Step 4: Call search_knowledge ─────────────────────────────────────────────

console.log("🔍 Calling search_knowledge('returns 45 days')...");
const knowledgeResult = await client.callTool({
    name: "search_knowledge",
    arguments: { query: "returns 45 days", source: "policies" },
});

if (knowledgeResult.isError) {
    console.error("❌ search_knowledge returned an error:", knowledgeResult.content);
    process.exit(1);
}

const knowledgeText = knowledgeResult.content[0]?.text ?? "";
const knowledge = JSON.parse(knowledgeText);
console.log(`   Found ${knowledge.found} result(s).`);
console.log("✅ search_knowledge succeeded.\n");

// ── Step 5: Call generate_evidence ───────────────────────────────────────────

console.log("📄 Calling generate_evidence(controls=[B.1.1, B.4.1])...");
const evidenceResult = await client.callTool({
    name: "generate_evidence",
    arguments: {
        partnerName: "Contoso (Smoke Test)",
        controls: ["B.1.1", "B.4.1"],
        solutionTitle: "Smoke Test Solution",
    },
});

if (evidenceResult.isError) {
    console.error("❌ generate_evidence returned an error:", evidenceResult.content);
    process.exit(1);
}

const evidenceText = evidenceResult.content[0]?.text ?? "";
if (!evidenceText.includes("B.1.1") || !evidenceText.includes("Module B")) {
    console.error("❌ generate_evidence output looks wrong:", evidenceText.slice(0, 200));
    process.exit(1);
}
console.log(`   Evidence doc: ${evidenceText.split("\n").length} lines generated.`);
console.log("✅ generate_evidence succeeded.\n");

// ── Done ──────────────────────────────────────────────────────────────────────

await client.close();

console.log("═══════════════════════════════════════════════════");
console.log("✅  SMOKE TEST PASSED — Zava MCP Server is healthy.");
console.log("═══════════════════════════════════════════════════");
console.log(`   Tools:  ${tools.length} registered`);
console.log(`   Data:   ${dataDir}`);
