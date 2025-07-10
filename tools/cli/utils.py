from textual import on
from textual.app import ComposeResult
from textual.widgets import Select, Label, Footer

from .screens import BaseScreen


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


__all__ = [
    "DefaultOrCustomApp",
]
