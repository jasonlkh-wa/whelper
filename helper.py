import pandas as pd
import os
import argparse
import logging


def dirname(file: str) -> str:
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


if __name__ == "__main__":
    print(help(pd.read_csv))
    pass
