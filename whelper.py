import pandas as pd
import os
import logging
import dotenv
import datetime

# CR-someday: Change the whelper to a module (__init__) instead of distributing one single file


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


import os
import shutil
import datetime


def backup_file_with_timestamp(file, backup_dir):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    file_name, file_extension = os.path.splitext(
        os.path.basename(file)
    )  # Get the file name and extension

    backup_file = f"{file_name}_{timestamp}{file_extension}"
    os.makedirs(backup_dir, exist_ok=True)
    shutil.copy2(file, os.path.join(backup_dir, backup_file))
    print(f"File '{file}' backed up as '{backup_file}' in '{backup_dir}'")


def backup_directory_with_timestamp(dir, ignore_set=None, ignore_hidden=True):
    """
    Creates a backup of the directory under [dir/.backup/<timestamp>].

    Args:
        dir (str): The directory to be backed up.
        ignore_set (list, optional): List of files or directories to be ignored during backup.
        ignore_hidden (bool, optional): Whether to ignore hidden files and directories.

    Returns:
        None
    """
    try:
        if not ignore_set:
            ignore_set = set()
        backup_dir = os.path.join(dir, ".backup")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_timestamp_dir = os.path.join(backup_dir, timestamp)

        if not os.path.exists(backup_dir):
            os.mkdir(backup_dir)

        os.mkdir(backup_timestamp_dir)

        for item in os.listdir(dir):
            if item != ".backup" and item not in ignore_set:
                if ignore_hidden and item.startswith("."):
                    continue
                item_path = os.path.join(dir, item)
                backup_item_path = os.path.join(backup_timestamp_dir, item)
                if os.path.isfile(item_path):
                    shutil.copy2(item_path, backup_item_path)
                else:
                    shutil.copytree(item_path, backup_item_path)
    except Exception as e:
        if os.path.exists(backup_timestamp_dir):
            shutil.rmtree(backup_timestamp_dir)
        print(
            f"Error backing up directory '{dir}'\nAll backup files created are removed.\n"
        )

        raise e
