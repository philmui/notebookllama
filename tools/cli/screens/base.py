from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Label, Footer

from ..config import COMMON_BINDINGS, SUBMIT_BINDING


class BaseScreen(Screen):
    """Base screen with common functionality for all screens."""

    BINDINGS = COMMON_BINDINGS

    def action_toggle_dark(self) -> None:
        self.app.theme = (
            "textual-dark" if self.app.theme == "textual-light" else "textual-light"
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


class ConfigurationScreen(BaseScreen):
    """Base screen provider configuration with submit functionality."""

    BINDINGS = BaseScreen.BINDINGS + [SUBMIT_BINDING]

    def action_submit(self) -> None:
        """To be implemented by specific provider screens"""
        pass
