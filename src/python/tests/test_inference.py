"""
Tests for the modular inference factory.

Verifies that the correct client type is created for each provider and
that missing configuration raises appropriate errors.
No network calls are made — clients are not invoked.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestInferenceFactory:
    """Verify create_chat_client returns correct client type per provider."""

    def test_github_provider_returns_openai_chat_client(self) -> None:
        """GitHub provider creates an OpenAIChatClient with custom base_url."""
        mock_openai_client = MagicMock()
        mock_chat_client = MagicMock()

        with (
            patch("openai.AsyncOpenAI", return_value=mock_openai_client),
            patch(
                "agent_framework.openai.OpenAIChatClient",
                return_value=mock_chat_client,
            ) as mock_cls,
        ):
            settings = MagicMock()
            settings.inference_provider = "github"
            settings.github_token = "ghp_test_token"
            settings.github_models_endpoint = "https://models.github.ai/inference"
            settings.github_models_chat_model = "openai/gpt-4o-mini"

            from app.inference.factory import create_chat_client

            result = create_chat_client(settings)

            assert result is mock_chat_client
            mock_cls.assert_called_once()
            call_kwargs = mock_cls.call_args
            assert call_kwargs.kwargs.get("model") == "openai/gpt-4o-mini"

    def test_unknown_provider_raises_value_error(self) -> None:
        """An unknown provider raises ValueError with the provider name."""
        settings = MagicMock()
        settings.inference_provider = "unknown-provider"

        from app.inference.factory import create_chat_client

        with pytest.raises(ValueError, match="unknown-provider"):
            create_chat_client(settings)

    def test_azure_openai_requires_endpoint(self) -> None:
        """Azure OpenAI provider raises RuntimeError when endpoint is missing."""
        settings = MagicMock()
        settings.inference_provider = "azure-openai"
        settings.azure_openai_endpoint = ""
        settings.azure_client_id = ""

        from app.inference.factory import create_chat_client

        with pytest.raises(RuntimeError, match="AZURE_OPENAI_ENDPOINT"):
            create_chat_client(settings)

    def test_foundry_requires_endpoint(self) -> None:
        """Foundry provider raises RuntimeError when endpoint is missing."""
        settings = MagicMock()
        settings.inference_provider = "foundry"
        settings.azure_ai_foundry_project_endpoint = ""
        settings.azure_client_id = ""

        from app.inference.factory import create_chat_client

        with pytest.raises(RuntimeError, match="AZURE_AI_FOUNDRY_PROJECT_ENDPOINT"):
            create_chat_client(settings)

    def test_embeddings_github_provider(self) -> None:
        """GitHub embeddings provider creates an AsyncOpenAI instance."""
        mock_client = MagicMock()
        with patch("openai.AsyncOpenAI", return_value=mock_client) as mock_cls:
            settings = MagicMock()
            settings.embeddings_provider = "github"
            settings.github_token = "ghp_test"
            settings.github_models_endpoint = "https://models.github.ai/inference"

            from app.inference.factory import create_embeddings_client

            result = create_embeddings_client(settings)

            assert result is mock_client
            mock_cls.assert_called_once()

    def test_embeddings_unknown_provider_raises(self) -> None:
        """Unknown embeddings provider raises ValueError."""
        settings = MagicMock()
        settings.embeddings_provider = "bad-provider"

        from app.inference.factory import create_embeddings_client

        with pytest.raises(ValueError, match="bad-provider"):
            create_embeddings_client(settings)


class TestSettings:
    """Verify Settings defaults and property logic."""

    def test_default_provider_is_github(self) -> None:
        from app.config import Settings

        s = Settings()
        assert s.inference_provider == "github"
        assert s.embeddings_provider == "github"

    def test_use_azure_stores_false_without_cosmos(self) -> None:
        from app.config import Settings

        s = Settings()
        assert not s.use_azure_stores

    def test_use_azure_stores_true_with_cosmos(self) -> None:
        from app.config import Settings

        s = Settings(cosmos_endpoint="https://test.documents.azure.com")
        assert s.use_azure_stores
