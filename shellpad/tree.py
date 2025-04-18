import os
import textual
from textual.widgets import DirectoryTree


class ShellTree(DirectoryTree):
    BINDINGS = [
        textual.binding.Binding("None", "", "Open script", key_display="Enter"),
    ]

    def __init__(self, path, *args, **kwargs):
        super().__init__(path, *args, **kwargs)

    async def _on_key(self, event: textual.events.Key) -> None:
        match event.key:
            case "enter":
                ...
            case "left":
                if os.path.isdir(self.cursor_node.data.path) and self.cursor_node.data.loaded is True:
                    self.action_select_cursor()
                    self.cursor_node.data.loaded = False
                else:
                    self.action_cursor_up()
            case "right":
                if os.path.isdir(self.cursor_node.data.path):
                    if self.cursor_node.data.loaded is True:
                        self.action_cursor_down()
                    else:
                        self.action_select_cursor()
                else:
                    self.action_select_cursor()
