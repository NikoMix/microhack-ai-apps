# syntax=docker/dockerfile:1

# ── Build stage ────────────────────────────────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

# Copy manifests first for layer-cache efficiency
COPY package*.json ./

# Install all dependencies (including dev for building)
RUN npm ci --ignore-scripts

# Copy source
COPY tsconfig.json ./
COPY src/ ./src/

# Compile TypeScript → dist/
RUN npm run build

# ── Runtime stage ──────────────────────────────────────────────────────────────
FROM node:22-alpine AS runtime

# Create non-root user — required by Container Apps security baseline
RUN addgroup -g 1001 -S mcp && \
    adduser  -u 1001 -S mcp -G mcp

WORKDIR /app

# Copy production manifest and install runtime-only deps
COPY package*.json ./
RUN npm ci --omit=dev --ignore-scripts && \
    npm cache clean --force

# Copy compiled output from build stage
COPY --from=builder /app/dist ./dist

# Copy seed data — the server reads this in HTTP mode
# (override DATA_DIR env var to use an external volume or Azure Blob mount)
COPY --chown=mcp:mcp ../../data ./data

USER mcp

# Port exposed by the HTTP/SSE transport (set MCP_PORT to override)
EXPOSE 3000

# Health check for Container Apps liveness probe
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:3000/health || exit 1

# Default: HTTP/SSE mode (STDIO is for local VS Code usage only)
ENV MCP_TRANSPORT=http
ENV MCP_PORT=3000
ENV DATA_DIR=/app/data

CMD ["node", "dist/index.js", "--http"]
