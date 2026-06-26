"""
Application configuration loaded from environment variables / .env file.

Env vars are defined in build-contract.md §3 (inference) and §6 (Azure resources).
See .env.example for a full template.
"""

from __future__ import annotations

import pathlib
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_data_dir() -> str:
    """Resolve the repo-level data/ directory relative to this file's location.

    Layout:  src/python/app/config.py
             ../../../../data/
    """
    here = pathlib.Path(__file__).parent  # app/
    python_root = here.parent  # src/python/
    src_root = python_root.parent  # src/
    repo_root = src_root.parent  # <repo-root>/
    candidate = repo_root / "data"
    return str(candidate) if candidate.exists() else str(python_root / "data")


class Settings(BaseSettings):
    """All runtime settings for the Zava Python API.

    Values are read (in priority order):
      1. Environment variables
      2. .env file in the current working directory
      3. Defaults defined here
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Inference providers ───────────────────────────────────────────────
    inference_provider: Literal["github", "azure-openai", "foundry"] = "github"
    embeddings_provider: Literal["github", "azure-openai", "foundry"] = "github"

    # ── GitHub Models ────────────────────────────────────────────────────
    github_token: str = ""
    github_models_endpoint: str = "https://models.github.ai/inference"
    github_models_chat_model: str = "openai/gpt-4o-mini"
    github_models_embedding_model: str = "openai/text-embedding-3-small"

    # ── Azure OpenAI ─────────────────────────────────────────────────────
    azure_openai_endpoint: str = ""
    azure_openai_chat_deployment: str = "gpt-4o-mini"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    azure_openai_api_version: str = "2025-04-01-preview"

    # ── Azure AI Foundry ─────────────────────────────────────────────────
    azure_ai_foundry_project_endpoint: str = ""
    azure_ai_foundry_chat_deployment: str = "gpt-4o-mini"

    # ── Azure infrastructure ─────────────────────────────────────────────
    cosmos_endpoint: str = ""
    cosmos_database: str = "zava"
    postgres_host: str = ""
    postgres_db: str = "zava"
    postgres_port: int = 5432
    postgres_user: str = "zava_app"
    azure_search_endpoint: str = ""
    azure_search_index: str = "zava-knowledge"
    azure_docintel_endpoint: str = ""
    azure_contentsafety_endpoint: str = ""
    azure_key_vault_endpoint: str = ""
    azure_client_id: str = ""  # user-assigned MI client ID

    # ── Observability ────────────────────────────────────────────────────
    applicationinsights_connection_string: str = ""

    # ── Local data directory ─────────────────────────────────────────────
    data_dir: str = ""  # resolved lazily in property below

    @property
    def resolved_data_dir(self) -> str:
        """Return the configured data directory, falling back to auto-detection."""
        return self.data_dir or _default_data_dir()

    @property
    def use_azure_stores(self) -> bool:
        """True when Cosmos DB is configured (Azure mode)."""
        return bool(self.cosmos_endpoint)

    @property
    def use_azure_search(self) -> bool:
        """True when Azure AI Search is configured."""
        return bool(self.azure_search_endpoint)

    @property
    def use_content_safety(self) -> bool:
        """True when Azure Content Safety is configured."""
        return bool(self.azure_contentsafety_endpoint)

    @property
    def use_document_intelligence(self) -> bool:
        """True when Azure Document Intelligence is configured."""
        return bool(self.azure_docintel_endpoint)


# Module-level singleton — imported by all other modules.
settings = Settings()
