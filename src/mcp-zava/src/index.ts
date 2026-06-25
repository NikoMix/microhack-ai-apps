/**
 * Zava MCP Server — entry point.
 *
 * Selects the transport mode at startup:
 *
 *   STDIO (default) — for VS Code / GitHub Copilot agent integration.
 *     Start: `node dist/index.js`
 *
 *   HTTP/SSE        — for Azure Container Apps deployment.
 *     Start: `node dist/index.js --http`
 *     Or:    MCP_TRANSPORT=http node dist/index.js
 *
 * The server name / version is sourced from package.json and registered
 * with the MCP SDK so clients can identify this server in `initialize` responses.
 */
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createZavaServer } from "./server.js";
import { startHttpServer } from "./transport/http.js";

// Detect HTTP mode from CLI flag or env var.
const useHttp =
    process.argv.includes("--http") ||
    process.env["MCP_TRANSPORT"] === "http";

// Build the server (loads data, registers all tools).
const server = await createZavaServer();

if (useHttp) {
    // Detached HTTP/SSE server — ideal for container deployments.
    await startHttpServer(server);
} else {
    // STDIO transport — standard for VS Code MCP and GitHub Copilot agent mode.
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("[zava-mcp] Running in STDIO mode. Ready for MCP client.");
}
