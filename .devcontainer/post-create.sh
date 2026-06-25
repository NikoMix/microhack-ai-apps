#!/usr/bin/env bash
# Post-create setup for the Zava AI MicroHack dev container.
set -euo pipefail

echo "==> Installing Marp CLI + markdownlint (slides & docs tooling)"
npm install -g @marp-team/marp-cli@latest markdownlint-cli2 || true

echo "==> Installing MkDocs Material (docs site)"
pip install --user mkdocs-material || true

echo "==> Installing Bicep CLI"
az bicep install || true

if [ -d src/python ]; then
  echo "==> Bootstrapping Python track"
  (cd src/python && python -m pip install --upgrade pip && (pip install -e ".[dev]" || pip install -r requirements-dev.txt || true))
fi

if [ -d src/dotnet ]; then
  echo "==> Restoring .NET track"
  (cd src/dotnet && dotnet restore || true)
fi

echo "==> Done. Set GITHUB_TOKEN (models:read) and run a track — see README.md"
