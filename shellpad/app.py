from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree, Footer
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

from utils import find_file_variants, load_script
from widgets import ShellTree, ShellTabs, ShellEditor, ShellTerminal


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
            yield ShellTree(self.path, extensions=self.extensions, id="shell_tree")
            yield Vertical(
                ShellTabs(id="shell_tabs"),
                ShellEditor(id="shell_editor"),
                ShellTerminal(id="shell_terminal"),
            )
        yield Footer()

    async def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        shell_editor = self.query_one("#shell_editor", ShellEditor)
        if event.path == self.selected_path:
            shell_editor.focus()
        self.selected_path = event.path

        if event.path not in self.scripts:
            variants = find_file_variants(event.path, as_dict=True)
            self.scripts[event.path] = {
                "path": event.path,
                "variants": {key: load_script(val) for key, val in variants.items()},
                "selected_id": list(variants.keys())[0],
            }

        await shell_editor.open_script(self.scripts[event.path])
