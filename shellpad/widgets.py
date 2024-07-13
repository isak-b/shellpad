import os
import asyncio
import subprocess

from textual import events
from textual.widgets import DirectoryTree, TextArea
from textual.binding import Binding

from utils import load_script, save_script


class ShellTree(DirectoryTree):
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
            script_editor = self.app.query_one("#script_editor", ShellEditor)
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


class ShellEditor(TextArea):
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
            script_tree = self.app.query_one("#script_tree", ShellTree)
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
        terminal = self.app.query_one("#terminal", ShellTerminal)
        await terminal.write(self.text, prefix=">", add_run_count=True)
        await asyncio.sleep(0.01)
        await terminal.run(self.text, prefix="", add_run_count=False)

    def action_save(self):
        terminal = self.app.query_one("#terminal", ShellTerminal)
        save_script(self.app.selected_path, self.text)
        terminal.write(f"Saved: {self.app.selected_path}")

    def action_reload(self):
        self.text = load_script(self.app.selected_path)

    def on_text_area_changed(self, _event: TextArea.Changed) -> None:
        if self.text != self.prev_text:
            self.app.scripts[self.app.selected_path] = self.text
            self.prev_text = self.text


class ShellTerminal(TextArea):
    async def on_mount(self):
        self.language = "bash"
        self.read_only = True
        self.run_count = 0

    async def write(self, text: str, prefix: str = "", add_run_count: bool = False):
        input_text = "".join([f"{prefix} {line}\n".lstrip() for line in str(text).split("\n") if line.strip() != ""])
        if add_run_count is True:
            input_text = f"\n[{self.run_count}]:\n{input_text}"
            self.run_count += 1
        self.text += input_text
        self.text = self.text.lstrip()
        self.scroll_end(animate=False)

    async def run(self, cmd: str, *args, **kwargs):
        result = subprocess.getoutput(cmd)
        await self.write(result, *args, **kwargs)

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
