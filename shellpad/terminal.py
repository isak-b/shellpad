import subprocess
import pydantic
import pathlib
import typing

import textual
from textual.widgets import TextArea


class Run(pydantic.BaseModel):
    command: str
    result: str
    metadata: str


class ShellTerminal(TextArea):
    async def on_mount(self):
        self.language = "bash"
        self.read_only = True
        self.runs: list[Run] = []

    async def action_run(self, cmd: str):
        if self.app.selected_path.suffix not in [".sh", ".py"]:
            return

        # Metadata
        metadata = f"[{len(self.runs)}]: {pathlib.Path(*self.app.selected_path.parts[1:])}"
        await self.action_write(metadata)

        # Command
        command = f"> {cmd}"
        await self.action_write(command)

        # Result
        res = None
        if self.app.selected_path.suffix == ".sh":
            res = subprocess.getoutput(cmd)
        elif self.app.selected_path.suffix == ".py":
            res = subprocess.run(["python3"], input=cmd, capture_output=True, encoding="UTF-8").stdout
        result = f"{res}"
        await self.action_write(result)
        await self.action_write("")

        # Add to runs
        self.runs.append(Run(command=command, result=result, metadata=metadata))

    async def action_write(self, msg):
        self.text += f"{msg}\n"
        self.scroll_end(animate=False)

    async def action_filter_messages(self, selected: list[typing.Literal["commands", "results"]]):
        self.text = ""
        for run in self.runs:
            await self.action_write(run.metadata)
            if "commands" in selected:
                await self.action_write(run.command)
            if "results" in selected:
                await self.action_write(run.result)
            await self.action_write("")

    def _on_key(self, event: textual.events.Key) -> None:
        if event.key == "up":
            if self.cursor_location == (0, 0):
                shell_menu = self.app.query_one("#shell_menu")
                # TODO: Focus the last option
                shell_menu.focus()
        if event.key == "down":
            if self.cursor_at_end_of_text:
                shell_tree = self.app.query_one("#shell_tree")
                shell_tree.focus()
