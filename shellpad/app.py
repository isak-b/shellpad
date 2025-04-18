import textual
from textual.widgets import DirectoryTree

from .menu import ShellMenu
from .tree import ShellTree
from .editor import ShellEditor
from .terminal import ShellTerminal


class ShellPad(textual.app.App):
    CSS_PATH = "static/styles.css"
    BINDINGS = [
        textual.binding.Binding("escape", "quit", "Quit", key_display="Esc"),
    ]

    def __init__(self):
        super().__init__()
        self.path = "./locations/git"
        self.selected_path = None

    def compose(self) -> textual.app.ComposeResult:
        yield textual.widgets.Header(show_clock=True)
        with textual.containers.Vertical():
            # TODO: Add more menu options, e.g., the range of terminal runs to show
            yield ShellMenu(id="shell_menu")
            yield ShellTerminal(id="shell_terminal")
            yield textual.containers.Horizontal(
                ShellTree(self.path, id="shell_tree"),
                ShellEditor(id="shell_editor"),
            )
        yield textual.widgets.Footer()

    async def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        shell_editor = self.query_one("#shell_editor", ShellEditor)
        if event.path == self.selected_path:
            shell_editor.focus()
        self.selected_path = event.path
        await shell_editor.action_open_script(self.selected_path)
