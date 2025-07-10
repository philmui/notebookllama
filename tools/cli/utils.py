from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Select, Input, Label, Footer


class BaseEmbeddingApp(App):
    CSS_PATH = "stylesheets/base.tcss"

    BINDINGS = [
        Binding(
            key="ctrl+q", action="quit", description="Submit", key_display="ctrl+q"
        ),
        Binding(
            key="ctrl+d",
            action="toggle_dark",
            description="Toggle Dark Theme",
            key_display="ctrl+d",
        ),
    ]

    def __init__(self):
        super().__init__()
        self.form_data = {}

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_quit(self) -> None:
        self.form_data = {
            input_id: self.query_one(f"#{input_id}", Input).value
            for input_id in self.get_input_ids()
        }
        self.exit()

    def get_input_ids(self) -> list[str]:
        """Override this to define input fields for the app"""
        return []


class DefaultOrCustomApp(BaseEmbeddingApp):
    def compose(self) -> ComposeResult:
        yield Label("How do you wish to proceed?", classes="form-title")
        yield Select(
            options=[
                ("With Default Settings", "With Default Settings"),
                ("With Custom Settings", "With Custom Settings"),
            ],
            prompt="Please select one of the following",
            classes="form-control",
        )
        yield Footer()

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.title = str(event.value)


class SelectEmbeddingApp(BaseEmbeddingApp):
    def compose(self) -> ComposeResult:
        yield Label("Embedding Model Selection", classes="form-title")
        yield Select(
            options=[
                ("OpenAI", "OpenAI"),
                ("Cohere", "Cohere"),
                ("HuggingFace API", "HuggingFace API"),
                ("Bedrock", "Bedrock"),
                ("Gemini", "Gemini"),
                ("Azure", "Azure"),
            ],
            prompt="Select the embedding model for your LlamaCloud Index",
            classes="form-control",
        )
        yield Footer()

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.title = str(event.value)


class BedrockEmbeddingApp(BaseEmbeddingApp):
    def compose(self) -> ComposeResult:
        yield Label("Model and API key", classes="form-title")
        yield Input(
            placeholder="AWS Region", type="text", id="region", classes="form-control"
        )
        yield Input(
            placeholder="AWS Secret Access Key",
            type="text",
            password=True,
            id="key_id",
            classes="form-control",
        )
        yield Footer()

    def get_input_ids(self) -> list[str]:
        return ["region", "key_id"]


class HuggingFaceEmbeddingApp(BaseEmbeddingApp):
    def compose(self) -> ComposeResult:
        yield Label("Model and API key", classes="form-title")
        yield Input(
            placeholder="API key",
            type="text",
            password=True,
            id="api_key",
            classes="form-control",
        )
        yield Input(
            placeholder="Model", type="text", id="model", classes="form-control"
        )
        yield Footer()

    def get_input_ids(self) -> list[str]:
        return ["api_key", "model"]


class OpenAIEmbeddingApp(BaseEmbeddingApp):
    def compose(self) -> ComposeResult:
        yield Label("Model and API key", classes="form-title")
        yield Input(
            placeholder="API key",
            type="text",
            password=True,
            id="api_key",
            classes="form-control",
        )
        yield Input(
            placeholder="Model", type="text", id="model", classes="form-control"
        )
        yield Footer()

    def get_input_ids(self) -> list[str]:
        return ["api_key", "model"]


class CohereEmbeddingApp(BaseEmbeddingApp):
    def compose(self) -> ComposeResult:
        yield Label("Model and API key", classes="form-title")
        yield Input(
            placeholder="API key",
            type="text",
            password=True,
            id="api_key",
            classes="form-control",
        )
        yield Input(
            placeholder="Model", type="text", id="model", classes="form-control"
        )
        yield Footer()

    def get_input_ids(self) -> list[str]:
        return ["api_key", "model"]


class AzureEmbeddingApp(BaseEmbeddingApp):
    def compose(self) -> ComposeResult:
        yield Label("Model and API key", classes="form-title")
        yield Input(
            placeholder="API key",
            type="text",
            password=True,
            id="api_key",
            classes="form-control",
        )
        yield Input(
            placeholder="Endpoint", type="text", id="target_uri", classes="form-control"
        )
        yield Footer()

    def get_input_ids(self) -> list[str]:
        return ["api_key", "target_uri"]


class GeminiEmbeddingApp(BaseEmbeddingApp):
    def compose(self) -> ComposeResult:
        yield Label("Model and API key", classes="form-title")
        yield Input(
            placeholder="API key",
            type="text",
            password=True,
            id="api_key",
            name="api_key",
            classes="form-control",
        )
        yield Footer()

    def get_input_ids(self) -> list[str]:
        return ["api_key"]


class OtherEmbeddingApp(BaseEmbeddingApp):
    def compose(self) -> ComposeResult:
        yield Label("Model and API key", classes="form-title")
        yield Input(
            placeholder="API key",
            type="text",
            password=True,
            id="api_key",
            name="api_key",
            classes="form-control",
        )
        yield Input(
            placeholder="Model name (or Endpoint URL for HF)",
            type="text",
            id="model",
            name="model",
            classes="form-control",
        )

        yield Footer()

    def get_input_ids(self) -> list[str]:
        return ["api_key", "model"]
