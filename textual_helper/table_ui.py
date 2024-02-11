from whelper.textual_helper.vim_data_table import VimDataTable, DetailCell
from whelper.textual_helper.prefix_enforce_validator import PrefixEnforceValidator
from whelper.t.record import Record
from textual.widgets import Footer, Header, Input, Log
from textual.binding import Binding
from textual.screen import Screen
from textual.app import ComposeResult
from textual.coordinate import Coordinate
import datetime
import csv
import pandas as pd
import json
import copy
import ast


# CR-someday: It is a know issue that "[n]" or alphabets with square brackets are unable to display.
# This is due to the textual library recognizing them as the terminal control sequences.
class TableUI(Screen):
    # CR-soon: docstring
    # CR-someday: there is some issue to the horizontal scroll bar outlook
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
        Binding("q", action="quit()", description="Quit", key_display="q"),
        Binding("f1", action="show_bindings()", description="Show bindings"),
        Binding(":", action="command_palette", description="Command Palette"),
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
        Binding(
            key="P",
            action="show_log()",
            description="show log",
            show=True,
            key_display="p",
        ),
    ]
    DELETE_MESSAGE = ":d please confirm (y/[n]): "
    ID_COL = "ID"
    ORIGINAL_ID_COL = "Original_ID"

    def __init__(
        self,
        data_or_path: (
            str | list[list[any]] | pd.DataFrame | dict[dict[any, any]] | None
        ) = None,
        with_header: bool = True,
        header: list | None = None,  # header, only valid when with_header is False
        name=None,
        id=None,
        editable_cols: set | None = None,  # set set("__") to disable
        column_widths: list | None = None,
        data_export_rate: int | None = None,  # in seconds
        col_separator: str = ",",
        enable_delete_row: bool = True,
        ignore_index: bool = False,
        index_col: str | None = None,
        is_export_data: bool = True,
        is_dev_for_pytest=False,
    ):
        super().__init__(name, id)

        self.data_or_path = data_or_path
        self.is_path = isinstance(data_or_path, str)
        self.file_type = (
            data_or_path[data_or_path.rindex(".") + 1 :] if self.is_path else None
        )
        self.source_data_type = type(data_or_path) if not self.is_path else None
        self.ignore_index = ignore_index

        raw_data = self.parse_data_or_path()

        self.header = (
            raw_data[0]
            if with_header
            else (header if header is not None else list(range(len(raw_data[0]))))
        )

        default_editable_cols = set(self.header)
        if ignore_index:
            default_editable_cols.remove(self.ID_COL)

        self.editable_cols = editable_cols or default_editable_cols

        self.data = raw_data[1:] if with_header else raw_data
        self.return_data = None  # this is not set when initialized, but later in [self.export_to_data_path]
        self.column_widths = column_widths or [None for _ in self.header]
        self.data_export_rate = data_export_rate
        self.col_separator = col_separator
        self.enable_delete_row = enable_delete_row
        self.index_col = index_col  # Unused for now
        self.is_export_data = is_export_data
        self._is_dev_for_pytest = is_dev_for_pytest  # set it to True only if this app is run by a pytest's [compare_snapshot]

    def get_indexed_nested_list_data_with_header(
        self, data: list[list[any]]
    ) -> list[list[any]]:
        indexed_data = []
        for idx, v in enumerate(data):
            if idx != 0:
                indexed_data.append([idx] + v)
            else:
                indexed_data.append([self.ID_COL] + v)

        return indexed_data

    def parse_dict_to_nested_list_data_with_header(
        self, data_dict: dict
    ) -> list[list[any]]:
        index_col = (
            [self.ID_COL, self.ORIGINAL_ID_COL] if self.ignore_index else [self.ID_COL]
        )
        header = index_col + [k for k in list(data_dict.values())[0].keys()]

        indexed_data = []
        if self.ignore_index:
            get_indexed_row = (
                lambda idx, key, record: [idx] + [key] + list(record.values())
            )
        else:
            get_indexed_row = lambda _idx, key, record: [key] + list(record.values())

        for idx, (key, record) in enumerate(data_dict.items()):
            row = get_indexed_row(idx, key, record)
            if len(row) == len(header):
                indexed_data.append(row)
            else:
                raise ValueError(
                    f"Data is not in tabula format. Header length: {len(header)}, row length at {idx}: {len(row)}"
                )

        return [header] + indexed_data

    def parse_data_or_path(self):

        if self.is_path:
            match self.file_type:
                case "csv":
                    with open(self.data_or_path, "r") as file:
                        csv_reader = csv.reader(file)

                        return (
                            self.get_indexed_nested_list_data_with_header(csv_reader)
                            if self.ignore_index
                            else list(csv_reader)
                        )

                case "json":
                    # CR-someday: add testing for the tabula validation
                    with open(self.data_or_path, "r") as file:
                        json_dict: dict = json.load(file)
                        return self.parse_dict_to_nested_list_data_with_header(
                            json_dict
                        )
                case _:
                    raise NotImplementedError
        else:
            if isinstance(self.data_or_path, pd.DataFrame):
                if self.ignore_index:
                    index = self.data_or_path.reset_index(drop=True).index
                    df = pd.concat(
                        [pd.DataFrame(index, columns=[self.ID_COL]), self.data_or_path],
                        axis=1,
                        join="outer",
                    )
                return [df.columns.tolist()] + df.values.tolist()
            elif isinstance(self.data_or_path, list) and isinstance(
                self.data_or_path[0], list
            ):
                return (
                    self.get_indexed_nested_list_data_with_header(self.data_or_path)
                    if self.ignore_index
                    else self.data_or_path
                )

            elif isinstance(self.data_or_path, dict) and isinstance(
                list(self.data_or_path.values())[0], dict
            ):
                return self.parse_dict_to_nested_list_data_with_header(
                    self.data_or_path
                )
            else:
                raise NotImplementedError

    def compose(self) -> ComposeResult:
        yield VimDataTable(id="table", cols=self.header)
        yield Input(id="input_field", disabled=True)
        yield Log(id="log")
        yield Header(show_clock=True if not self._is_dev_for_pytest else False)
        yield Footer()

    # CR-someday: think of separating the add row function out so that
    # users can easily amend the [on_mount], refer to [cli-tools/tood]
    # when changing the function
    def on_mount(self) -> None:
        table = self.query_one("#table", VimDataTable)

        for i, width in zip(self.header, self.column_widths):
            table.add_column(i, width=width, key=i)

        for idx, row_values in enumerate(self.data):
            row_values = [str(i) for i in row_values]
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
        log = self.query_one("#log", Log)
        self.app.push_screen(DetailCell(log.lines))
        log.clear()

    def action_show_bindings(self):
        self.app.push_screen(
            DetailCell(
                [f"{binding.key}: {binding.description}" for binding in self.BINDINGS]
            )
        )

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
    def on_input_submitted(
        self,
    ):

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

    def get_data_as_nested_list(self):
        res = []

        # this is the header defined by the file in [self.header] with ["ID"]
        # removed as it is generated by this class
        table = self.query_one("#table", VimDataTable)
        header_without_numeric_index = copy.deepcopy(self.header)

        if self.ignore_index:
            header_without_numeric_index.pop(
                header_without_numeric_index.index(self.ID_COL)
            )

        res.append(header_without_numeric_index)

        value_idx_to_be_exported = [
            self.header.index(i) for i in header_without_numeric_index
        ]  # although [1:] can also remove the ID column, this impl would potentially provide more flexibility for the future
        for idx in range(table.row_count):
            row = table.get_row_at(idx)
            res.append([row[i] for i in value_idx_to_be_exported])

        return header_without_numeric_index, res

    def convert_data_with_header_to_dict(
        self, data_with_header: list[list[str]], header_without_numeric_index: list
    ):
        if self.ignore_index:
            header_without_numeric_index.pop(
                header_without_numeric_index.index(self.ORIGINAL_ID_COL)
            )  # ORIGINAL_ID_COL will be the top level key of the dictionary instead of a column/field

        data_without_header = data_with_header[1:]
        data_dict = {
            row[0]: {k: v for k, v in zip(header_without_numeric_index, row[1:])}
            for row in data_without_header
        }
        for idx, record in data_dict.items():
            for k, v in record.items():
                if v and v[0] == "{":
                    data_dict[idx][k] = json.loads(v.replace("'", '"'))
                else:
                    try:
                        data_dict[idx][k] = ast.literal_eval(v)
                    except (SyntaxError, ValueError):
                        pass

        return data_dict

    def export_to_data_path(self):
        # CR: all export should try to eval the value, or may store the original type?
        header, data_with_header = self.get_data_as_nested_list()

        if self.is_path:
            self.return_data = (
                data_with_header  # app return value if file path is passed
            )
            if not self.is_export_data:
                return None
            # CR-soon: may be separate the file_path vs source data handling to two functions
            match self.file_type:
                case "csv":
                    with open(self.data_or_path, "r") as file:
                        original_data = list(csv.reader(file))
                    try:
                        with open(self.data_or_path, "w") as file:
                            for row in data_with_header:
                                csv.writer(file).writerow(row)

                        self.log_message("Data auto-saved successfully!")

                    except Exception as e:
                        with open(self.data_or_path, "w") as file:
                            csv.writer(file).writerows(original_data)
                        error_message = (
                            f"Error occured while saving data, nothing done! {e}"
                        )
                        self.log_message(error_message)
                        return e
                case "json":
                    # CR-someday: consider not hard-coding the index as 0 for future scalability
                    # CR-soon: this should be tested carefully
                    data_dict = self.convert_data_with_header_to_dict(
                        data_with_header, header
                    )

                    with open(self.data_or_path, "r") as file:
                        original_data = json.load(file)

                    try:
                        with open(self.data_or_path, "w") as file:
                            json.dump(data_dict, file, indent=4)
                    except Exception as e:
                        with open(self.data_or_path, "w") as file:
                            json.dump(original_data, file, indent=4)

                        error_message = (
                            f"Error occured while saving data, nothing done! {e}"
                        )
                        self.log_message(error_message)
                        return e

                case _:
                    raise NotImplementedError
        else:  # source_data is used
            match self.source_data_type():
                case pd.DataFrame():
                    # CR-soon: add test for the return_value
                    self.return_data = pd.DataFrame(
                        data_with_header[1:], columns=data_with_header[0]
                    )
                case (
                    list()
                ):  # CR-soon: make it to detect 1-level nested list (may have higher ordered nested list in the future)
                    self.return_data = data_with_header
                case dict():
                    self.return_data = self.convert_data_with_header_to_dict(
                        data_with_header, header
                    )
                case _:
                    raise NotImplementedError

    async def action_quit(self):
        e = self.export_to_data_path()
        if isinstance(e, Exception):
            raise e
        self.app.exit(self.return_data)
