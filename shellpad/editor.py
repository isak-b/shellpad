import textual
from textual.widgets import TextArea

from .utils import load_script, save_script


class ShellEditor(TextArea):
    BINDINGS = [
        textual.binding.Binding("escape", "", "Close script", key_display="Esc"),
        textual.binding.Binding("ctrl+enter", "run", "Run", key_display="ctrl+Enter"),
        textual.binding.Binding("ctrl+s", "save", "Save", key_display="ctrl+S"),
        textual.binding.Binding("ctrl+r", "reload", "Reload", key_display="ctrl+R"),
    ]

    async def on_mount(self):
        self.language = "bash"
        self.show_line_numbers = True
        self.scripts = {}

    async def action_open_script(self, selected_path):
        if selected_path not in self.scripts:
            self.text = load_script(selected_path)
            self.scripts[selected_path] = self.text
        else:
            self.text = self.scripts[selected_path]

    async def action_run(self):
        shell_terminal = self.app.query_one("#shell_terminal")
        row, _ = self.cursor_location
        text = self.get_text_range((row, 0), (row + 1, 0)).rstrip()
        if text:
            await shell_terminal.action_run(text)

    async def action_save(self):
        shell_terminal = self.app.query_one("#shell_terminal")
        save_script(self.app.selected_path, self.text)
        await shell_terminal.action_write(f"Saved: {self.app.selected_path}")

    def action_reload(self):
        self.text = load_script(self.app.selected_path)

    def on_text_area_changed(self):
        self.scripts[self.app.selected_path] = self.text

    def _on_key(self, event: textual.events.Key) -> None:

        if event.key == "escape":
            shell_tree = self.app.query_one("#shell_tree")
            shell_tree.focus()
        if event.key == "up":
            if self.cursor_location == (0, 0):
                shell_terminal = self.app.query_one("#shell_terminal")
                shell_terminal.focus()
        if event.key == "left":
            if self.cursor_location == (0, 0):
                shell_tree = self.app.query_one("#shell_tree")
                shell_tree.focus()
            else:
                self.action_cursor_left()
        else:
            return
        event.prevent_default()
