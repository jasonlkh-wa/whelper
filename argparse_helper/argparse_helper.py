from whelper import setup_main_logger
import argparse
import logging


"""
CR: complete this section and give example of [MainArgParser]'s 
add_all_subparsers_from_dict(self, subparser_dict)
Expected Usage:

"""


class SubtoolParser:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __call__(self, subparsers: argparse._SubParsersAction):
        self.parser: argparse.ArgumentParser = subparsers.add_parser(
            self.name,
            help=self.description,
            description=self.description,
        )

        self.parser.add_argument(
            "-dev",
            required=False,
            help="<optional> enable dev mode",
            action="store_true",
        )
        return self.parser


class MainArgParser:
    """
    A class for generating an argument parser for a command-line tool.

    Args:
        prog (str): The name of the program.
        subparser_description (str, optional): The description for the subparsers. Defaults to "the tool list".
        subparser_name (str, optional): The name for the subparsers. Defaults to "tool".
        description (str, optional): The description for the argument parser. Defaults to "select the tool to be used".
    """

    def __init__(
        self,
        prog: str,
        subparser_description: str = "",
        subparser_name: str = "tool",
        description: str = "Select the tool to be used",
        logger: logging.Logger | None = None,
    ):
        # Create an argument parser with the given program name and description
        self.parser = argparse.ArgumentParser(prog=prog, description=description)
        self.subparser_name = subparser_name
        # Add subparsers to the argument parser
        self.subparsers = self.parser.add_subparsers(
            title=subparser_name,
            dest=subparser_name,
            description=subparser_description,
            required=True,
        )

        self.subparser_to_function_dict = dict()
        self.logger = logger or setup_main_logger()

    def parse_args(self):
        return self.parser.parse_args()

    def add_subparser(
        self,
        subparser: SubtoolParser,
    ):
        subparser(self.subparsers)

    def add_all_subparsers_from_dict(self, subparser_dict):
        """
        Adds all the subparsers from a dictionary to the main parser.

        Parameters:
            subparser_dict (dict): A dictionary containing the subparsers. Each key is the name of the subparser, and each value is a dictionary with two keys:
                - 'parser' (ArgumentParser): The subparser object.
                - 'function' (function): The function associated with the subparser.

        Returns:
            None
        """
        for name, subparser in subparser_dict.items():
            self.add_subparser(subparser["parser"])
            self.subparser_to_function_dict[name] = subparser["function"]

    def call_subtool(
        self,
        args: argparse.Namespace,
    ):
        if getattr(args, self.subparser_name) in self.subparser_to_function_dict.keys():
            return self.subparser_to_function_dict.get(
                getattr(args, self.subparser_name)
            )(args)
        else:
            fail_message = (
                f"Invalid tool argument: {getattr(args, self.subparser_name)}"
            )

            if self.logger is not None:
                self.logger.warning(fail_message)
            else:
                raise ValueError(fail_message)
