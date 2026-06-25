# `mcp-zava` — Zava AI Agent Platform MCP Server

Custom **Model Context Protocol (MCP)** server for the Zava AI MicroHack. It exposes
Zava's seed data and tools over MCP so they can be consumed by:

- **GitHub Copilot** (via `.vscode/mcp.json` or `mcp.json` at the repo root)
- **VS Code chat agents** in agent mode
- **Azure Container Apps** (azd service `mcp-zava`, HTTP/SSE transport)
- **Python / .NET agent tracks** in the lab (direct MCP tool calls)

## Tools

| Tool | Description | Used by agent |
|---|---|---|
| `get_product` | Retrieve a product by ID | Concierge, Merchandiser |
| `search_products` | Full-text + category product search | Merchandiser |
| `get_order` | Retrieve an order by ID | Concierge |
| `get_inventory` | Stock levels with low-stock alerts | Operations |
| `get_customers` | Zava business unit records (B.2.2) | Operations, Trust |
| `search_knowledge` | RAG over policies + supplier docs | Concierge, Operations |
| `generate_evidence` | Assemble Module B evidence skeleton | Trust (Lab 6 capstone) |

## Quick-start — GitHub Models mode (free, no Azure required)

```bash
# 1. Install dependencies
cd src/mcp-zava
npm install

# 2. Build TypeScript
npm run build

# 3. Run in STDIO mode (picked up by VS Code via mcp.json)
npm start

# 4. Run in HTTP/SSE mode (port 3000)
npm run start:http
```

No environment variables are required for local usage — the server reads the
`data/` seed files from the repository root automatically.

### Optional env vars

| Variable | Default | Description |
|---|---|---|
| `DATA_DIR` | `data/` at repo root | Absolute path to the seed data directory |
| `MCP_TRANSPORT` | `stdio` | Set to `http` to start the HTTP/SSE server |
| `MCP_PORT` | `3000` | HTTP listen port |

## Running the smoke test

The smoke test builds the server, connects as an MCP client, lists all tools,
and makes three tool calls to verify correctness.

```bash
cd src/mcp-zava
npm run smoke-test
```

Expected output (abridged):

```
🔨 Building Zava MCP Server...
✅ Build succeeded.

🔌 Connecting to Zava MCP Server (STDIO)...
✅ Connected.

📋 Listing tools...
   Found 7 tool(s):
   ✅ get_product
   ✅ search_products
   ✅ get_order
   ✅ get_inventory
   ✅ get_customers
   ✅ search_knowledge
   ✅ generate_evidence

✅ All 7 expected tools are registered.

📦 Calling get_product(ZAVA-RUN-001)...
   • Name:     Pulse Smart Running Shirt
   • Price:    $89
   ...

✅ SMOKE TEST PASSED — Zava MCP Server is healthy.
```

## Azure mode — deploy with azd

The `mcp-zava` service in `azure.yaml` points to this directory. When `azd up`
provisions the stack:

1. Container Apps builds the image from this `Dockerfile`.
2. `DATA_DIR=/app/data` is set automatically (seed data is `COPY`-d in).
3. The HTTP/SSE endpoint is available at the Container App's FQDN on port 3000.

Update `mcp.json` at the repo root with the deployed URL to switch VS Code
and Copilot to the cloud server:

```json
{
  "mcpServers": {
    "zava": {
      "type": "sse",
      "url": "https://<mcp-zava-fqdn>/sse"
    }
  }
}
```

## Docker (standalone)

```bash
# Build image (run from repo root so data/ is in build context)
docker build -t zava-mcp -f src/mcp-zava/Dockerfile .

# Run locally
docker run -p 3000:3000 zava-mcp

# Health check
curl http://localhost:3000/health
```

## Architecture

```
mcp-zava/
├── src/
│   ├── index.ts          Entry point — selects STDIO or HTTP transport
│   ├── server.ts         McpServer + all 7 tool definitions
│   ├── data/
│   │   └── loader.ts     Reads JSON + Markdown files from data/
│   └── transport/
│       └── http.ts       Express-based SSE transport
├── smoke-test.mjs        Automated smoke test (STDIO client)
├── Dockerfile            Non-root, multi-stage; azd-compatible
├── package.json
└── tsconfig.json
```

## Quality gates

```bash
npm run typecheck   # zero TypeScript errors
npm run lint        # ESLint (typescript-eslint recommended)
npm audit           # zero moderate+ vulnerabilities
npm run smoke-test  # builds + tests 7 tools
```
