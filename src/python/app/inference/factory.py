"""
Modular inference factory for the Zava AI Agent Platform.

Selects the chat-completion and embedding backend at runtime via:
  - INFERENCE_PROVIDER  = github | azure-openai | foundry   (default: github)
  - EMBEDDINGS_PROVIDER = github | azure-openai | foundry   (default: github)

Build contract: .microhack/build-contract.md §3.

Design
------
All three providers expose an OpenAI-compatible chat API, so we create an
``openai.AsyncOpenAI`` (or ``AsyncAzureOpenAI``) client and wrap it in the
Agent Framework's ``OpenAIChatClient``.

For GitHub Models, the endpoint is https://models.github.ai/inference with a
GitHub PAT as the API key.

For Azure OpenAI and Foundry, we use ``DefaultAzureCredential`` (Managed
Identity in production) — no API key ever appears in code.

The embedding client is also provider-switched; it always uses the
``text-embedding-3-small`` model (1536 dimensions) as required by the contract.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def create_chat_client(settings: Any) -> Any:
    """Return a configured Agent Framework chat client for the active provider.

    Parameters
    ----------
    settings:
        The app ``Settings`` singleton (passed in to avoid circular imports).

    Returns
    -------
    An ``OpenAIChatClient`` (or provider-equivalent) instance for use with
    ``Agent(client=...)``.
    """
    provider = settings.inference_provider
    logger.info("Creating chat client for provider: %s", provider)

    if provider == "github":
        return _github_chat_client(settings)
    if provider == "azure-openai":
        return _azure_openai_chat_client(settings)
    if provider == "foundry":
        return _foundry_chat_client(settings)
    msg = f"Unknown INFERENCE_PROVIDER: {provider!r}"
    raise ValueError(msg)


def create_embeddings_client(settings: Any) -> Any:
    """Return a configured OpenAI-compatible embeddings client.

    The returned object exposes ``embeddings.create(input=..., model=...)``
    matching the ``openai.AsyncOpenAI`` interface.
    """
    provider = settings.embeddings_provider
    logger.info("Creating embeddings client for provider: %s", provider)

    if provider == "github":
        return _github_embeddings_client(settings)
    if provider == "azure-openai":
        return _azure_openai_embeddings_client(settings)
    if provider == "foundry":
        return _azure_openai_embeddings_client(settings)  # Foundry reuses AOAI for embeddings
    msg = f"Unknown EMBEDDINGS_PROVIDER: {provider!r}"
    raise ValueError(msg)


# ── GitHub Models ─────────────────────────────────────────────────────────────


def _github_chat_client(settings: Any) -> Any:
    """GitHub Models — OpenAI-compatible endpoint with GITHUB_TOKEN as API key."""
    import openai
    from agent_framework.openai import OpenAIChatClient

    if not settings.github_token:
        logger.warning(
            "GITHUB_TOKEN is not set. Chat requests will fail. "
            "/health and /agents will still respond."
        )

    raw = openai.AsyncOpenAI(
        base_url=settings.github_models_endpoint,
        api_key=settings.github_token or "no-token",  # SDK requires a non-empty value
    )
    return OpenAIChatClient(
        model=settings.github_models_chat_model,
        async_client=raw,
    )


def _github_embeddings_client(settings: Any) -> Any:
    """GitHub Models — embeddings endpoint (same base URL as chat)."""
    import openai

    return openai.AsyncOpenAI(
        base_url=settings.github_models_endpoint,
        api_key=settings.github_token or "no-token",
    )


# ── Azure OpenAI ──────────────────────────────────────────────────────────────


def _azure_openai_chat_client(settings: Any) -> Any:
    """Azure OpenAI — uses DefaultAzureCredential (no API key)."""
    import openai
    from agent_framework.openai import OpenAIChatClient
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    if not settings.azure_openai_endpoint:
        msg = "AZURE_OPENAI_ENDPOINT must be set for azure-openai provider"
        raise RuntimeError(msg)

    credential = DefaultAzureCredential(managed_identity_client_id=settings.azure_client_id or None)
    token_provider = get_bearer_token_provider(
        credential,
        "https://cognitiveservices.azure.com/.default",
    )
    raw = openai.AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        azure_ad_token_provider=token_provider,
        api_version=settings.azure_openai_api_version,
    )
    return OpenAIChatClient(
        model=settings.azure_openai_chat_deployment,
        async_client=raw,
    )


def _azure_openai_embeddings_client(settings: Any) -> Any:
    """Azure OpenAI embeddings client (DefaultAzureCredential)."""
    import openai
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    if not settings.azure_openai_endpoint:
        msg = "AZURE_OPENAI_ENDPOINT must be set for azure-openai embeddings provider"
        raise RuntimeError(msg)

    credential = DefaultAzureCredential(managed_identity_client_id=settings.azure_client_id or None)
    token_provider = get_bearer_token_provider(
        credential,
        "https://cognitiveservices.azure.com/.default",
    )
    return openai.AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        azure_ad_token_provider=token_provider,
        api_version=settings.azure_openai_api_version,
    )


# ── Azure AI Foundry ──────────────────────────────────────────────────────────


def _foundry_chat_client(settings: Any) -> Any:
    """Azure AI Foundry — uses agent-framework-foundry's FoundryChatClient.

    Falls back to Azure OpenAI-compatible client if the Foundry package is
    not installed (e.g., during local development without the full stack).
    """
    if not settings.azure_ai_foundry_project_endpoint:
        msg = "AZURE_AI_FOUNDRY_PROJECT_ENDPOINT must be set for foundry provider"
        raise RuntimeError(msg)

    try:
        from agent_framework_foundry import FoundryChatClient
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential(
            managed_identity_client_id=settings.azure_client_id or None
        )
        return FoundryChatClient(
            endpoint=settings.azure_ai_foundry_project_endpoint,
            deployment=settings.azure_ai_foundry_chat_deployment,
            credential=credential,
        )
    except ImportError:
        logger.warning(
            "agent-framework-foundry not available; "
            "using Azure OpenAI client against Foundry endpoint."
        )
        return _foundry_via_azure_openai(settings)


def _foundry_via_azure_openai(settings: Any) -> Any:
    """Fallback: hit the Foundry endpoint using the AzureOpenAI-compatible client."""
    import openai
    from agent_framework.openai import OpenAIChatClient
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    credential = DefaultAzureCredential(managed_identity_client_id=settings.azure_client_id or None)
    token_provider = get_bearer_token_provider(
        credential,
        "https://cognitiveservices.azure.com/.default",
    )
    raw = openai.AsyncAzureOpenAI(
        azure_endpoint=settings.azure_ai_foundry_project_endpoint,
        azure_ad_token_provider=token_provider,
        api_version="2025-04-01-preview",
    )
    return OpenAIChatClient(
        model=settings.azure_ai_foundry_chat_deployment,
        async_client=raw,
    )
