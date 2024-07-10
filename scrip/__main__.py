import os
import sys
import asyncio
import subprocess
import yaml

from textual import events
from textual.app import App, ComposeResult
from textual.widgets import DirectoryTree, TextArea, Footer
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CFG_PATH = os.path.join(ROOT_PATH, "config.yaml")


def load_cfg(path: str):
    return yaml.safe_load(open(path, "r"))


def load_script(path: str):
    return open(path, "r").read()


def save_script(path: str, content: str):
    with open(path, "w") as f:
        f.write(content)


class ScriptTree(DirectoryTree):
    BINDINGS = [
        Binding("None", "", "Open script", key_display="Enter"),
    ]

    def __init__(self, path, extensions, *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        self.extensions = extensions

    async def _on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            ...
        elif event.key == "ctrl+enter":
            script_editor = self.app.query_one("#script_editor", ScriptEditor)
            await script_editor.action_run()
        elif event.key == "left":
            if os.path.isdir(self.cursor_node.data.path) and self.cursor_node.data.loaded is True:
                self.action_select_cursor()
                self.cursor_node.data.loaded = False
            else:
                self.action_cursor_up()
        elif event.key == "right":
            if os.path.isdir(self.cursor_node.data.path):
                if self.cursor_node.data.loaded is True:
                    self.action_cursor_down()
                else:
                    self.action_select_cursor()
            else:
                self.action_select_cursor()

    def filter_paths(self, paths: list) -> list:
        output = []
        for path in paths:
            if os.path.isdir(path):
                valid_dir = False
                for _, _, files in os.walk(path):
                    for file in files:
                        if any(file.endswith(ext) for ext in self.extensions):
                            valid_dir = True
                if valid_dir is True:
                    output.append(path)
            elif any(path.name.endswith(ext) for ext in self.extensions):
                output.append(path)
        return output


class ScriptEditor(TextArea):
    BINDINGS = [
        Binding("escape", "", "Close script", key_display="Esc"),
        Binding("ctrl+enter", "run", "Run", key_display="ctrl+Enter"),
        Binding("ctrl+s", "save", "Save", key_display="ctrl+S"),
        Binding("ctrl+r", "reload", "Reload", key_display="ctrl+R"),
    ]

    async def on_mount(self):
        self.language = "bash"
        self.show_line_numbers = True
        self.prev_text = ""

    def _on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            script_tree = self.app.query_one("#script_tree", ScriptTree)
            script_tree.focus()
        if event.key == "left":
            if self.cursor_location == (0, 0):
                self.screen.focus_previous()
        if event.key == "right":
            if self.cursor_at_end_of_text:
                self.screen.focus_next()
        if event.key == "down":
            if self.cursor_at_end_of_text:
                self.screen.focus_next()
            else:
                self.action_cursor_down()
        else:
            return
        event.prevent_default()

    async def action_run(self):
        terminal = self.app.query_one("#terminal", Terminal)
        await terminal.async_write(self.text, prefix=">", add_run_count=True)
        await asyncio.sleep(0.01)
        await terminal.async_run(self.text, prefix="", add_run_count=False)

    def action_save(self):
        terminal = self.app.query_one("#terminal", Terminal)
        save_script(self.app.selected_path, self.text)
        terminal.write(f"Saved: {self.app.selected_path}")

    def action_reload(self):
        self.text = load_script(self.app.selected_path)

    def on_text_area_changed(self, _event: TextArea.Changed) -> None:
        if self.text != self.prev_text:
            self.app.scripts[self.app.selected_path] = self.text
            self.prev_text = self.text


class Terminal(TextArea):
    async def on_mount(self):
        self.language = "bash"
        self.read_only = True
        self.run_count = 0

    def write(self, text: str, prefix: str = "", add_run_count: bool = False):
        input_text = "".join([f"{prefix} {line}\n".lstrip() for line in str(text).split("\n") if line.strip() != ""])
        if add_run_count is True:
            input_text = f"\n[{self.run_count}]:\n{input_text}"
            self.run_count += 1
        self.text += input_text
        self.text = self.text.lstrip()
        self.scroll_end(animate=False)

    async def async_write(self, *args, **kwargs):
        self.write(*args, **kwargs)

    def run(self, cmd: str, *args, **kwargs):
        result = subprocess.getoutput(cmd)
        self.write(result, *args, **kwargs)

    async def async_run(self, *args, **kwargs):
        self.run(*args, **kwargs)

    def _on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if self.cursor_location == (0, 0):
                self.screen.focus_previous()
            else:
                self.action_cursor_up()
        elif event.key == "left":
            if self.cursor_location == (0, 0):
                self.screen.focus_previous()
            else:
                self.action_cursor_left()


class Scriptify(App):
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
            yield ScriptTree(self.path, extensions=self.extensions, id="script_tree")
            yield Vertical(
                ScriptEditor(id="script_editor"),
                Terminal(id="terminal"),
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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = load_cfg(sys.argv[1])
    else:
        path = os.getcwd()

    cfg = load_cfg(DEFAULT_CFG_PATH)
    app = Scriptify(path=path, cfg=cfg)
    app.run()
