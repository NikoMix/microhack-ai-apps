/**
 * HTTP / SSE transport adapter for the Zava MCP Server.
 *
 * Exposes the MCP server over HTTP so it can be deployed as an
 * Azure Container App (azd service `mcp-zava`).
 *
 * Endpoints:
 *   GET  /health          — liveness probe (Container Apps)
 *   GET  /sse             — open an SSE stream (MCP SSE transport)
 *   POST /messages?sessionId=... — client → server messages
 *
 * The SSE transport is the widely-supported transport for web-hosted MCP
 * servers and is compatible with VS Code (via the `url` type in mcp.json).
 */
import express, { type Request, type Response } from "express";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

/** Active SSE transport sessions, keyed by session ID. */
const sessions = new Map<string, SSEServerTransport>();

export async function startHttpServer(server: McpServer): Promise<void> {
    const app = express();
    app.use(express.json({ limit: "4mb" }));

    const port = parseInt(process.env.MCP_PORT ?? "3000", 10);

    // ── Health check ──────────────────────────────────────────────────────────
    // Container Apps calls this for liveness + readiness probes.
    app.get("/health", (_req: Request, res: Response) => {
        res.json({ status: "ok", server: "zava-mcp", version: "1.0.0" });
    });

    // ── SSE endpoint — client opens this to establish a session ───────────────
    app.get("/sse", async (req: Request, res: Response) => {
        const transport = new SSEServerTransport("/messages", res);
        sessions.set(transport.sessionId, transport);

        res.on("close", () => {
            sessions.delete(transport.sessionId);
            console.error(`[zava-mcp] SSE session ${transport.sessionId} closed`);
        });

        console.error(`[zava-mcp] New SSE session: ${transport.sessionId}`);
        await server.connect(transport);
    });

    // ── Messages endpoint — client posts JSON-RPC messages here ──────────────
    app.post("/messages", async (req: Request, res: Response) => {
        const sessionId = req.query["sessionId"] as string | undefined;
        if (!sessionId) {
            res.status(400).json({ error: "Missing sessionId query parameter" });
            return;
        }

        const transport = sessions.get(sessionId);
        if (!transport) {
            res.status(404).json({ error: `Session '${sessionId}' not found or expired` });
            return;
        }

        await transport.handlePostMessage(req, res, req.body);
    });

    // ── Start listening ───────────────────────────────────────────────────────
    await new Promise<void>((resolve, reject) => {
        app
            .listen(port, () => {
                console.error(
                    `[zava-mcp] HTTP/SSE server listening on :${port}\n` +
                    `  Health:   GET  http://localhost:${port}/health\n` +
                    `  SSE:      GET  http://localhost:${port}/sse\n` +
                    `  Messages: POST http://localhost:${port}/messages?sessionId=<id>`
                );
                resolve();
            })
            .on("error", reject);
    });
}
