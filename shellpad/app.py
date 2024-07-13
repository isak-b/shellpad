from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree, TextArea, Footer
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

from utils import load_script
from widgets import ShellTree, ShellEditor, ShellTerminal


class ShellPad(App):
    CSS_PATH = "static/styles.css"
    BINDINGS = [
        Binding("escape", "quit", "Quit", key_display="Esc"),
    ]

    def __init__(self, path: str, cfg: dict):
        super().__init__()
        self.path = path
        self.cfg = cfg
        self.extensions = cfg["extensions"]
        self.selected_path = None
        self.scripts = {}

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield ShellTree(self.path, extensions=self.extensions, id="script_tree")
            yield Vertical(
                ShellEditor(id="script_editor"),
                ShellTerminal(id="terminal"),
            )
        yield Footer()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        script_editor = self.query_one("#script_editor", TextArea)
        if event.path not in self.scripts:
            self.scripts[event.path] = load_script(event.path)
        script_editor.text = self.scripts[event.path]
        if event.path == self.selected_path:
            script_editor.focus()
        self.selected_path = event.path
