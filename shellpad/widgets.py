import os
import asyncio
import subprocess
from pathlib import PosixPath
from typing import Iterator

from textual import events
from textual.widgets import DirectoryTree, TextArea, Tabs
from textual.binding import Binding

from utils import load_script, save_script, is_valid_dir, is_valid_file


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
            shell_editor = self.app.query_one("#shell_editor", ShellEditor)
            await shell_editor.action_run()
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

    def filter_paths(self, paths: Iterator[PosixPath]) -> list:
        """Removes invalid dirs and files from paths
        NOTE:
        - paths is a generator that yields a list of PosixPath objects (pointing to dirs and paths) in the current dir
        - be aware that filtering may fail without raising an exception if the path is treated as str
        """

        output = []
        for path in paths:
            if path.is_dir() and is_valid_dir(str(path), extensions=self.extensions):
                output.append(path)
            elif path.is_file() and is_valid_file(
                str(path), extensions=self.extensions, hide_file_variants=self.app.cfg["hide_file_variants"]
            ):
                output.append(path)
        return output


class ShellTabs(Tabs):
    def create_new_tabs(self, ids: list):
        self.clear()
        for i in ids:
            self.add_tab(f"[{i}]")


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
            shell_tree = self.app.query_one("#shell_tree", ShellTree)
            shell_tree.focus()
        if event.key == "up":
            if self.cursor_location == (0, 0):
                self.screen.focus_previous()
        if event.key == "left":
            if self.cursor_location == (0, 0):
                self.screen.focus_previous()
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
        shell_terminal = self.app.query_one("#shell_terminal", ShellTerminal)
        await shell_terminal.write(self.text, prefix=">", add_run_count=True)
        await asyncio.sleep(0.01)
        await shell_terminal.run(self.text, prefix="", add_run_count=False)

    def action_save(self):
        shell_terminal = self.app.query_one("#shell_terminal", ShellTerminal)
        save_script(self.app.selected_path, self.text)
        shell_terminal.write(f"Saved: {self.app.selected_path}")

    def action_reload(self):
        self.text = load_script(self.app.selected_path)

    async def open_script(self, script: dict):
        tabs = self.app.query_one("#shell_tabs", ShellTabs)
        tabs.create_new_tabs(script["variants"].keys())
        selected_id = self.app.scripts[self.app.selected_path]["selected_id"]
        self.text = script["variants"][selected_id]

    def on_text_area_changed(self, _event: TextArea.Changed) -> None:
        if self.text != self.prev_text:
            selected_id = self.app.scripts[self.app.selected_path]["selected_id"]
            self.app.scripts[self.app.selected_path]["variants"][selected_id] = self.text
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
