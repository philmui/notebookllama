from textual.app import ComposeResult
from textual.widgets import Input

from llama_index.embeddings.openai import OpenAIEmbedding
from llama_cloud import PipelineCreateEmbeddingConfig_OpenaiEmbedding

from ..base import ConfigurationScreen


class OpenAIEmbeddingScreen(ConfigurationScreen):
    """Configuration screen for OpenAI embeddings."""

    def get_title(self) -> str:
        return "OpenAI Embedding Configuration"

    def get_form_elements(self) -> list[ComposeResult]:
        return [
            Input(
                placeholder="API key",
                type="text",
                password=True,
                id="api_key",
                classes="form-control",
            ),
            Input(
                placeholder="Model",
                type="text",
                id="model",
                classes="form-control",
            ),
        ]

    def action_submit(self) -> None:
        """Handle form submission by creating OpenAI embedding configuration."""
        api_key = self.query_one("#api_key", Input).value
        model = self.query_one("#model", Input).value

        embed_model = OpenAIEmbedding(model=model, api_key=api_key)
        embedding_config = PipelineCreateEmbeddingConfig_OpenaiEmbedding(
            type="OPENAI_EMBEDDING",
            component=embed_model,
        )

        self.app.config = embedding_config

        self.app.handle_completion(self.app.config)
