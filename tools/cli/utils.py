import os
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Select, Input, Label, Footer
from dataclasses import dataclass
from typing import Optional


COMMON_BINDINGS = [
    Binding("ctrl+q", "quit", "Exit", key_display="ctrl+q"),
    Binding("ctrl+d", "toggle_dark", "t", key_display="ctrl+d"),
]
SUBMIT_BINDING = Binding("ctrl+s", "submit", "Submit", key_display="ctrl+s")


@dataclass
class EmbeddingConfig:
    provider: str
    api_key: Optional[str] = None
    model: Optional[str] = None
    region: Optional[str] = None
    key_id: Optional[str] = None


class BaseScreen(Screen):
    BINDINGS = COMMON_BINDINGS

    def action_toggle_dark(self) -> None:
        self.app.theme = (
            "textual-dark" if self.app.theme != "textual-light" else "textual-light"
        )

    def action_quit(self) -> None:
        self.app.exit()

    def compose(self) -> ComposeResult:
        yield Container(
            Label(self.get_title(), classes="form-title"),
            *self.get_form_elements(),
            Footer(),
            classes="form-container",
        )

    def get_title(self) -> str:
        return "Base Screen"

    def get_form_elements(self) -> list:
        return []


class InitialScreen(BaseScreen):
    def get_title(self) -> str:
        return "How do you wish to proceed?"

    def get_form_elements(self) -> list:
        return [
            Select(
                options=[
                    ("With Default Settings", "With Default Settings"),
                    ("With Custom Settings", "With Custom Settings"),
                ],
                prompt="Please select one of the following",
                id="setup_type",
                classes="form-control",
            )
        ]

    @on(Select.Changed, "#setup_type")
    def handle_selection(self, event: Select.Changed) -> None:
        app = self.app
        if isinstance(app, EmbeddingSetupApp):
            app.config.setup_type = event.value
            self.handle_next()

    def handle_next(self) -> None:
        app = self.app
        if isinstance(app, EmbeddingSetupApp):
            if app.config.setup_type == "With Default Settings":
                app.handle_default_setup()
            else:
                app.push_screen(ProviderSelectScreen(app.config))


class ProviderSelectScreen(BaseScreen):
    def get_title(self) -> str:
        return "Select an embedding provider"

    def get_form_elements(self) -> list:
        return [
            Select(
                options=[
                    ("OpenAI", "OpenAI"),
                    ("Cohere", "Cohere"),
                    ("Bedrock", "Bedrock"),
                    ("HuggingFace", "HuggingFace"),
                    ("Azure", "Azure"),
                    ("Gemini", "Gemini"),
                    ("Other", "Other"),
                ],
                prompt="Please select an embedding provider",
                classes="form-control",
                id="provider_select",
            )
        ]

    @on(Select.Changed, "#provider_select")
    def handle_selection(self, event: Select.Changed) -> None:
        app = self.app
        if isinstance(app, EmbeddingSetupApp):
            app.config.provider = event.value
            self.handle_next()

    def handle_next(self) -> None:
        app = self.app
        if isinstance(app, EmbeddingSetupApp):
            provider_screens = {
                "OpenAI": OpenAIEmbeddingScreen
                # "Cohere": CohereEmbeddingScreen,
                # "Bedrock": BedrockEmbeddingScreen,
                # "HuggingFace": HuggingFaceEmbeddingScreen,
                # "Azure": AzureEmbeddingScreen,
                # "Gemini": GeminiEmbeddingScreen,
                # "Other": OtherEmbeddingScreen,
            }
            screen_class = provider_screens.get(app.config.provider)
            if screen_class:
                app.push_screen(screen_class(app.config))


class ConfigurationScreen(BaseScreen):
    BINDINGS = BaseScreen.BINDINGS + [SUBMIT_BINDING]

    def action_submit(self) -> None:
        """To be implemented by specific provider screens"""
        pass


class OpenAIEmbeddingScreen(ConfigurationScreen):
    def get_title(self) -> str:
        return "OpenAI Embedding Configuration"

    def get_form_elements(self) -> list:
        return [
            Input(
                placeholder="API key",
                type="text",
                password=True,
                id="api_key",
                classes="form-control",
            ),
            Input(placeholder="Model", type="text", id="model", classes="form-control"),
        ]

    def action_submit(self) -> None:
        self.app.config.api_key = self.query_one("#api_key", Input).value
        self.app.config.model = self.query_one("#model", Input).value
        self.app.handle_completion(self.app.config)


class EmbeddingSetupApp(App):
    CSS_PATH = "stylesheets/base.tcss"

    def __init__(self):
        super().__init__()
        self.config = EmbeddingConfig(provider="")

    def on_mount(self) -> None:
        self.push_screen(InitialScreen())

    def handle_completion(self, config: EmbeddingConfig) -> None:
        self.exit(config)

    def handle_default_setup(self) -> None:
        self.config.provider = "OpenAI"
        self.config.api_key = os.getenv("OPENAI_API_KEY")
        self.config.model = "text-embedding-3-small"

    def get_input_ids(self) -> list[str]:
        """Override this to define input fields for the app"""
        return []


class DefaultOrCustomApp(BaseScreen):
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


class SelectEmbeddingApp(BaseScreen):
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


class BedrockEmbeddingApp(BaseScreen):
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


class HuggingFaceEmbeddingApp(BaseScreen):
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


class OpenAIEmbeddingApp(BaseScreen):
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


class CohereEmbeddingApp(BaseScreen):
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


class AzureEmbeddingApp(BaseScreen):
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


class GeminiEmbeddingApp(BaseScreen):
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


class OtherEmbeddingApp(BaseScreen):
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
