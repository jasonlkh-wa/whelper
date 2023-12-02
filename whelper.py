import pandas as pd
import os
import logging
import dotenv


def dirname(file: str) -> str:
    """Returns the directory name of a given file path."""
    return os.path.expanduser(os.path.dirname(file))


def load_and_describe_df(path: str, sheet_name=0) -> pd.DataFrame:
    """Read a dataframe based on the filetype, describe and return the dataframe."""
    accepted_file_extensions = ["csv", "parquet", "xlsx", "xlsm"]

    user_input_type = path[path.rindex(".") + 1 :]

    if user_input_type not in ["xlsx", "xlsm"] and sheet_name != 0:
        print(
            "Unused argument sheet_name, this is applicable to xlsx or xlsm files only."
        )

    match user_input_type:
        case "csv":
            df = pd.read_csv(path)
        case "parquet":
            df = pd.read_parquet(path)
        case "xlsx" | "xlsm":
            df = pd.read_excel(path, sheet_name=sheet_name)
        case _:
            raise ValueError(
                f"File type: {user_input_type}\nOnly accept the following file extension: {', '.join(accepted_file_extensions)}"
            )

    print(df.describe())
    return df


def mach(x: str):
    """Replaces spaces and hyphens in a string with underscores."""
    return x.replace(" ", "_").replace("-", "_")


def setup_main_logger():
    logger = logging.getLogger("main_logger")
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def setup_logger_and_pwd(file):
    # ----------------- Configure logger -----------------
    logger = logging.getLogger("main_logger")

    # ----------------- Base file paths ------------------
    dotenv.load_dotenv()
    PWD = dirname(file)

    return logger, PWD


format_codes = {
    "format": {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m]",
        "italic": "\033[3m",
        "underline": "\033[4m",
        "strikethrough": "\033[9m",
        "reverse": "\033[7m",
    },
    "foreground_color": {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    },
    "background_color": {
        "black": "\033[40m",
        "red": "\033[41m",
        "green": "\033[42m",
        "yellow": "\033[43m",
        "blue": "\033[44m",
        "magenta": "\033[45m",
        "cyan": "\033[46m",
        "white": "\033[47m",
        "default": "\033[49m",
    },
}


def get_highlight_string(x, format: list = ["reset"], fg="yellow", bg="default") -> str:
    """
    Generate a highlighted string with specified formatting options.

    Args:
        x (Any): The string to be highlighted.
        format (list, optional): A list of formatting options. Defaults to ["reset"].
        fg (str, optional): The foreground color. Defaults to "yellow".
        bg (str, optional): The background color. Defaults to "default".

    Returns:
        str: The highlighted string.

    """
    prefix = (
        "".join([f"{format_codes['format'][i]}" for i in format])
        + format_codes["foreground_color"][fg]
        + format_codes["background_color"][bg]
    )
    return f"{prefix}{x}\033[0m"


def investigate(x):
    """Prints the type and value of the input string."""
    printls(f"type: {type(x)}\nvalue:\n {x=}")


def printls(x: str, n=50):
    """Print a line separator followed by the input string and another line separator."""
    line_separator = "-" * n
    print(f"{line_separator}\n{x}\n{line_separator}")