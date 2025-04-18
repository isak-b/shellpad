import textual


class ShellMenu(textual.widgets.SelectionList):
    async def on_mount(self):
        self.add_options(
            (
                ("commands", "commands", True),
                ("results", "results", True),
            ),
        )
        self.border_title = "Show:"

    async def on_selection_list_selected_changed(self, event):
        shell_terminal = self.app.query_one("#shell_terminal")
        await shell_terminal.action_filter_messages(self.selected)

    def _on_key(self, event: textual.events.Key) -> None:
        if event.key == "down":
            if self.highlighted == self.option_count - 1:
                shell_terminal = self.app.query_one("#shell_terminal")
                shell_terminal.focus()
