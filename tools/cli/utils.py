from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Select, Input, Label, Footer


class DefaultOrCustomApp(App):
    CSS_PATH = "stylesheets/select.tcss"
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

    def compose(self) -> ComposeResult:
        yield Label("How do you wish to proceed?", id="label1")
        yield Select(
            options=[
                ("With Default Settings", "With Default Settings"),
                ("With Custom Settings", "With Custom Settings"),
            ],
            prompt="Please select one of the following",
        )
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.title = str(event.value)


class SelectEmbeddingApp(App):
    CSS_PATH = "stylesheets/select.tcss"
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

    def compose(self) -> ComposeResult:
        yield Label("Embedding Model Selection", id="label1")
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
        )
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.title = str(event.value)


class BedrockEmbeddingApp(App):
    CSS_PATH = "stylesheets/input.tcss"
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

    def compose(self) -> ComposeResult:
        yield Label("Model and API key", id="label1")
        yield Input(placeholder="AWS Region", type="text", id="region")
        yield Input(
            placeholder="AWS Secret Access Key", type="text", password=True, id="key_id"
        )
        yield Input(
            placeholder="AWS Secret Key ID", type="text", password=True, id="api_key"
        )
        yield Input(placeholder="Model", type="text", id="model")
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_quit(self) -> None:
        # Capture form data before quitting
        self.form_data = {
            "region": self.query_one("#region", Input).value,
            "key_id": self.query_one("#key_id", Input).value,
            "api_key": self.query_one("#api_key", Input).value,
            "model": self.query_one("#model", Input).value,
        }
        self.exit()


class AzureEmbeddingApp(App):
    CSS_PATH = "stylesheets/input.tcss"
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

    def compose(self) -> ComposeResult:
        yield Label("Model and API key", id="label1")
        yield Input(placeholder="API key", type="text", password=True, id="api_key")
        yield Input(placeholder="Endpoint", type="text", id="target_uri")
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_quit(self) -> None:
        # Capture form data before quitting
        self.form_data = {
            "api_key": self.query_one("#api_key", Input).value,
            "target_uri": self.query_one("#target_uri", Input).value,
        }
        self.exit()


class GeminiEmbeddingApp(App):
    CSS_PATH = "stylesheets/input.tcss"
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

    def compose(self) -> ComposeResult:
        yield Label("Model and API key", id="label1")
        yield Input(
            placeholder="API key",
            type="text",
            password=True,
            id="api_key",
            name="api_key",
        )
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_quit(self) -> None:
        # Capture form data before quitting
        self.form_data = {
            "api_key": self.query_one("#api_key", Input).value,
        }
        self.exit()


class OtherEmbeddingApp(App):
    CSS_PATH = "stylesheets/input.tcss"
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

    def compose(self) -> ComposeResult:
        yield Label("Model and API key", id="label1")
        yield Input(
            placeholder="API key",
            type="text",
            password=True,
            id="api_key",
            name="api_key",
        )
        yield Input(
            placeholder="Model name (or Endpoint URL for HF)",
            type="text",
            id="model",
            name="model",
        )
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_quit(self) -> None:
        # Capture form data before quitting
        self.form_data = {
            "api_key": self.query_one("#api_key", Input).value,
            "model": self.query_one("#model", Input).value,
        }
        self.exit()


if __name__ == "__main__":

    def default():
        print("Default settings chosen")

    app1 = DefaultOrCustomApp()
    app1.run()

    if app1.title == "With Default Settings":
        default()
    else:
        app2 = SelectEmbeddingApp()
        app2.run()

        if app2.title == "Azure":
            app3 = AzureEmbeddingApp()
            app3.run()
            print(f"API Key: {app3.form_data.get('api_key', '')}")
            print(f"Target URI: {app3.form_data.get('target_uri', '')}")

        elif app2.title == "Bedrock":
            app4 = BedrockEmbeddingApp()
            app4.run()
            print(f"API Key: {app4.form_data.get('api_key', '')}")
            print(f"Key ID: {app4.form_data.get('key_id', '')}")
            print(f"Region: {app4.form_data.get('region', '')}")
            print(f"Model: {app4.form_data.get('model', '')}")

        elif app2.title == "Gemini":
            app5 = GeminiEmbeddingApp()
            app5.run()
            print(f"API Key: {app5.form_data.get('api_key', '')}")

        else:
            app6 = OtherEmbeddingApp()
            app6.run()
            print(f"API Key: {app6.form_data.get('api_key', '')}")
            print(f"Model: {app6.form_data.get('model', '')}")
