from textual.widgets import DataTable, Label, Footer, Header
from textual.binding import Binding
from textual.screen import Screen
from textual.app import ComposeResult


class VimDataTable(DataTable):
    BINDINGS = [
        Binding(key="j", action="cursor_down", description="Move down", show=False),
        Binding(key="k", action="cursor_up", description="Move up", show=False),
        Binding(key="l", action="cursor_right", description="Move right", show=False),
        Binding(key="h", action="cursor_left", description="Move left", show=False),
        Binding(
            key="p",
            action="show_cell_detail()",
            description="Show details",
            show=True,
        ),
    ]

    def __init__(self, cols, name=None, id=None):
        super().__init__(name=name, id=id)
        self.cols = cols

    def action_show_cell_detail(self):
        cursor_row_values = [
            list(i) for i in zip(self.cols, self.get_row_at(self.cursor_row))
        ]

        if self.name != "ROW_DETAILS":
            self.app.push_screen(DetailText(cursor_row_values))


class DetailText(Screen):
    BINDINGS = [
        Binding(
            key="backspace, q",
            action="app.pop_screen",
            description="Back",
            show=True,
        ),
    ]

    def __init__(self, values, name=None, id=None):
        super().__init__(name, id)
        self.values = values
        self.cols = ["col", "details"]
        self.columns_width = [10, 50]

    def compose(self) -> ComposeResult:
        yield VimDataTable(id="details", cols=self.cols, name="ROW_DETAILS")
        yield Header(show_clock=True)
        yield Footer()

    def on_mount(self) -> None:
        details = self.query_one("#details", VimDataTable)
        for i, width in zip(self.cols, self.columns_width):
            details.add_column(i, width=width)

        for row in self.values:
            details.add_row(*row, height=max([len(i) // 50 + 1 for i in row]))
