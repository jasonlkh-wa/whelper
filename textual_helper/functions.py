import textual
from whelper.textual_helper.table_ui import *


def display_table(data: list[list] | pd.DataFrame, is_dev_for_pytest=False):
    """Display the data in a textual table."""

    class TableDisplay(textual.app.App):
        BINDINGS = [
            textual.binding.Binding(
                key="R", action="refresh_screen", description="Refresh screen"
            )
        ]

        def push_table(self):
            self.push_screen(
                TableUI(
                    source_data=data,
                    id="table",
                    enable_delete_row=False,
                    editable_cols=set("__"),
                    ignore_index=True,
                    is_dev_for_pytest=is_dev_for_pytest,
                )
            )

        def on_mount(self) -> None:
            self.push_table()

        def action_refresh_screen(self):
            self.pop_screen()
            self.push_table()

    app = TableDisplay()
    app.run()
    return TableDisplay
