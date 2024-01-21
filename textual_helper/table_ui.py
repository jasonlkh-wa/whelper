from .vim_data_table import VimDataTable
from .prefix_enforce_validator import PrefixEnforceValidator
from textual.widgets import Footer, Header, Input, Log
from textual.binding import Binding
from textual.screen import Screen
from textual.app import ComposeResult
from textual.coordinate import Coordinate
import datetime
import csv


# CR-someday: the method override for some textual built in function
# does not work well, e.g. when [on_mount] is overrided in a new class,
# textual will call both [TableUI.on_mount] and [NewClass.on_mount]
#
# One of the temporary solution is to think of a way to easily edit the
# [on_mount] and [on_input_submit] method.
#
# For [on_mount], the user would edit the function because they may want to
# 1. preprocess the data before adding it
# 2. add some custom columns apart from the columns from data source
#
# For [on_input_submit], the function can be refactored so that the user can
# have custom dictionary to match [pattern:function] for the function
#
# please consider separating these functions in two part, one part is the
# [on_mount]/[on_input_submit] which should not be overrided
# (consider checking if the user define these two methods, raise a warning for that)
# and the other part is method that hold some preprocessing/custom column definition/
# [pattern:function] matching
class TableUI(Screen):
    DEFAULT_CSS = """
    TablueUI {
        align: left top;
        background: black;
        color: white;
        height: 1fr;
    }

    #table {
        height: 1fr;
    }

    #table > .datatable--header {
        text-style: bold;
        background: #1f618d;
    }

    #table > .datatable--cursor {
        background: #f39c12 30%;
    }

    #input_field {
        padding: 0 1 0 1;
        margin: 0 -1 0 -1;
    }

    #input_field:focus {
        border: tall #ffffff;
    }

    #log {
        height: 1;
        align: left bottom;
        background: #f39c12;
        color: #000000;
        padding: 0 0 0 1;
        overflow: hidden scroll;  
    }
    """
    BINDINGS = [
        ("q", "quit()", "Quit"),
        (":", "command_palette", "Command Palette"),
        Binding(key="A", action="add_row()", description="Add row", show=True),
        Binding(
            key="escape",
            action="off_input_focus()",
            description="Off input_field focus",
            show=False,
        ),
        Binding(
            key="D", action="delete_current_row()", description="Delete", show=True
        ),
        Binding(key="E", action="edit_cell()", description="Edit", show=True),
    ]
    DELETE_MESSAGE = ":d please confirm (y/[n]): "

    def __init__(
        self,
        data_path: str,
        with_header: bool = True,
        header: list | None = None,
        name=None,
        id=None,
        editable_cols: set | None = None,
        column_widths: list | None = None,
        data_export_rate: int | None = None,
        col_separator: str = ",",
        enable_delete_row: bool = True,
        use_default_on_mount: bool = True,
        use_default_on_submit: bool = True,
    ):
        super().__init__(name, id)
        self.data_path = data_path
        self.file_type = data_path[data_path.rindex(".") + 1 :]
        raw_data = self.parse_data_file(data_path, self.file_type)
        self.header = raw_data[0] if with_header else header
        self.editable_cols = editable_cols or set(self.header)
        self.data = raw_data[1:] if with_header else raw_data
        self.column_widths = column_widths or [None for _ in self.header]
        self.data_export_rate = data_export_rate
        self.col_separator = col_separator
        self.enable_delete_row = enable_delete_row
        self.use_default_on_mount = use_default_on_mount  # as [on_mount] method cannot be override, a bool is used to control the override
        self.use_default_on_submit = use_default_on_submit  # as [on_submit] method cannot be override, a bool is used to control the override

    def parse_data_file(self, data_path, file_type):
        data = []
        match file_type:
            case "csv":
                with open(data_path, "r") as file:
                    csv_reader = csv.reader(file)
                    for row in csv_reader:
                        data.append(row)
            case _:
                raise NotImplementedError

        return data

    def compose(self) -> ComposeResult:
        yield VimDataTable(id="table", cols=self.header)
        yield Input(id="input_field", disabled=True)
        yield Log(id="log")
        yield Header(show_clock=True)
        yield Footer()

    # CR-someday: think of separating the add row function out so that
    # users can easily amend the [on_mount], refer to [cli-tools/tood]
    # when changing the function
    def on_mount(self) -> None:
        if not self.use_default_on_mount:
            return None

        table = self.query_one("#table", VimDataTable)

        for i, width in zip(self.header, self.column_widths):
            table.add_column(i, width=width, key=i)

        for idx, row_values in enumerate(self.data):
            table.add_row(*row_values, key=idx)

        # Periodically export data to data_path for backup
        if self.data_export_rate:
            self.set_interval(
                self.data_export_rate, self.export_to_data_path, pause=False
            )

    def focus_input_field(self, message: str = "", suffix_pattern: str | None = None):
        input_field = self.query_one("#input_field", Input)
        input_field.disabled = False

        input_field.validators = [
            PrefixEnforceValidator(
                prefix=message,
                input_field=input_field,
                suffix_pattern=suffix_pattern,
            )
        ]

        input_field.value = message
        input_field.focus()

    def action_add_row(self):
        self.focus_input_field(":a ")

    def log_message(self, *message):
        log = self.query_one("#log", Log)
        log.write_lines(
            [f"{datetime.datetime.now().strftime('%H:%M:%S')} | {' '.join(message)}"]
        )

    def add_row(self, message: str):
        table = self.query_one("#table", VimDataTable)

        try:
            row_data = message.split(self.col_separator)
        except ValueError:
            self.log_message(f"Invalid input")
            return
        if len(row_data) != len(self.header):
            self.log_message(
                f"Number of columns doesn't match, {len(row_data)} != expected {len(self.header)}"
            )
            return
        table.add_row(*row_data)
        self.log_message(f"New row added successfully!")

    def _truncate(self, s, length=20):
        return s[:length] + ".." if len(s) > length else s

    def action_delete_current_row(self):
        if not self.enable_delete_row:
            self.log_message("Delete row is disabled")
            return

        table = self.query_one("#table", VimDataTable)
        if table.row_count > 0:
            cursor_row = table.cursor_row
            row_values = [self._truncate(i, 20) for i in table.get_row_at(cursor_row)]
            self.log_message(f"delete {row_values}? y/[n]")

            self.focus_input_field(self.DELETE_MESSAGE, suffix_pattern="[yn]{1}")

    def delete_row(self, message: str):
        if not self.enable_delete_row:
            self.log_message("Delete row is disabled")
            return

        if message.lower() == "y":
            table = self.query_one("#table", VimDataTable)
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key

            table.remove_row(row_key)
            self.log_message(f"Record deleted successfully!")
        elif message.lower() == "n":
            self.log_message(f"Nothing done.")
        else:
            self.log_message(f"Invalid choice, nothing done.")

    def action_edit_cell(self):
        table = self.query_one("#table", VimDataTable)

        cursor_coordinate = Coordinate(table.cursor_row, table.cursor_column)
        cursor_header = table.coordinate_to_cell_key(cursor_coordinate).column_key.value

        current_value = table.get_cell_at(cursor_coordinate)
        if cursor_header in self.editable_cols:
            self.log_message(f"editing - {self._truncate(current_value, 20)}")
            self.focus_input_field(
                f":edit <{table.cursor_row};{table.cursor_column}> -> "
            )
        else:
            self.log_message(f"{cursor_header} is not editable")

    def action_show_log(self):
        pass

    def edit_cell(self, message: str, validate=None):
        table = self.query_one("#table", VimDataTable)
        # parse the coordinate to edit
        row, col = message[message.index("<") + 1 : message.index(">")].split(";")
        coordinate = Coordinate(int(row), int(col))

        new_value = message[message.index("->") + 2 :].strip()
        table.update_cell_at(coordinate, new_value)

        self.log_message(f"Cell value updated successfully!")

    def remove_prefix_enforce_validators(self, input_field: Input | None = None):
        input_field = (
            self.query_one("#input_field", input_field)
            if not input_field
            else input_field
        )
        if input_field.validators:
            for i in input_field.validators:
                if isinstance(i, PrefixEnforceValidator):
                    input_field.validators.remove(i)

    def action_off_input_focus(self):
        self.remove_prefix_enforce_validators()

        input_field = self.query_one("#input_field", Input)
        if input_field.value:
            log = self.query_one("#log", Log)
            log.write_lines(" ")
            input_field.value = ""
        input_field.disabled = True

    # CR-someday: think of a better way for users to easily add new condiion
    # to the function instead of overriding the whole function,
    # a dict with [pattern:function] may help
    def on_input_submitted(self):
        if not self.use_default_on_submit:
            return None

        input_field = self.query_one("#input_field", Input)
        if input_field.value.startswith(":a "):
            self.add_row(input_field.value[3:])
        elif input_field.value.startswith(self.DELETE_MESSAGE):
            self.delete_row(input_field.value.split(" ")[-1])
        elif input_field.value.startswith(":edit "):
            self.edit_cell(input_field.value[6:])
        else:
            self.log_message(f"Invalid command <{input_field.value}>, nothing done")

        self.remove_prefix_enforce_validators()

        input_field.value = ""
        input_field.disabled = True

    def export_to_data_path(self):
        table = self.query_one("#table", VimDataTable)
        match self.file_type:
            case "csv":
                with open(self.data_path, "w") as file:
                    csv.writer(file).writerow(self.header)
                    for idx in range(table.row_count):
                        # this assume the new columns added must be placed after the original columns in data file
                        row = table.get_row_at(idx)[: len(self.header)]
                        csv.writer(file).writerow(row)
            case _:
                raise NotImplementedError

    async def action_quit(self):
        self.export_to_data_path()
        await self.app.action_quit()
