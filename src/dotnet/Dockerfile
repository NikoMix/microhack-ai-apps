# ── Stage 1: build ────────────────────────────────────────────────────────────
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Copy solution and project files first for layer caching
COPY Zava.sln ./
COPY Zava.Api/Zava.Api.csproj Zava.Api/
COPY Zava.Tests/Zava.Tests.csproj Zava.Tests/
RUN dotnet restore

# Copy source
COPY Zava.Api/ Zava.Api/
COPY Zava.Tests/ Zava.Tests/

# Build and test
RUN dotnet test --no-restore --configuration Release
RUN dotnet publish Zava.Api/Zava.Api.csproj \
    --no-restore \
    --configuration Release \
    --output /app/publish \
    /p:UseAppHost=false

# ── Stage 2: runtime (non-root, distroless-style) ─────────────────────────────
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime

# Non-root user (UID 1000) required for Azure Container Apps security policy
RUN addgroup --system --gid 1000 appgroup \
 && adduser --system --uid 1000 --ingroup appgroup appuser

WORKDIR /app

# Copy published application
COPY --from=build /app/publish ./

# Copy seed data alongside the app so the default path resolution works
COPY --from=build /src/../../../data ./data

# Environment defaults (overridden at runtime via env vars or Key Vault refs)
ENV ASPNETCORE_URLS=http://+:8080 \
    ASPNETCORE_ENVIRONMENT=Production \
    INFERENCE_PROVIDER=github \
    EMBEDDINGS_PROVIDER=github

# Switch to non-root user
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q --spider http://localhost:8080/health || exit 1

ENTRYPOINT ["dotnet", "Zava.Api.dll"]
