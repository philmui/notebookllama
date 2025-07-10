from textual.binding import Binding

COMMON_BINDINGS = [
    Binding("ctrl+q", "quit", "Exit", key_display="ctrl+q"),
    Binding("ctrl+d", "toggle_dark", "Toggle Dark Theme", key_display="ctrl+d"),
]

SUBMIT_BINDING = Binding("ctrl+s", "submit", "Submit", key_display="ctrl+s")
