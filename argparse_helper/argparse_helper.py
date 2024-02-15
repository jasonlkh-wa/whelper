from whelper import setup_main_logger
import argparse
import logging


"""
CR-soon: complete this section and give example of [MainArgParser]'s 
add_all_subparsers_from_dict(self, subparser_dict)
Expected Usage:

"""


# CR: think of a way to let [SubtoolParser] inherit [MainParser] so
# that the class can iteratively define
class SubtoolParser:
    """
    CR-soon: docstring
    """

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.subparser = argparse.ArgumentParser(
            add_help=False
        )  # this is a dummy parser to contain the args

        self.subparser.add_argument(
            "--dev",
            required=False,
            help="<optional> enable dev mode",
            action="store_true",
        )

    def __call__(self, subparsers: argparse._SubParsersAction):
        self.parser: argparse.ArgumentParser = subparsers.add_parser(
            self.name,
            help=self.description,
            description=self.description,
            parents=[self.subparser],
        )

        return self.parser


class MainArgParser:
    """
    A class for generating an argument parser for a command-line tool.

    Args:
        prog (str): The name of the program.
        subparser_description (str, optional): The description for the subparsers. Defaults to "the tool list".
        subparsers_name (str, optional): The name for the subparsers. Defaults to "tool".
        description (str, optional): The description for the argument parser. Defaults to "select the tool to be used".
        logger (logging.Logger | None, optional): The logger object for logging messages/warnings. Defaults to None \
                                                    (a new logger will be created if None).

    Attributes:
        parser (argparse.ArgumentParser): The argument parser object.
        subparsers_name (str): The name for the subparsers.
        subparsers (argparse._SubParsersAction): The subparsers object for adding subcommands.
        subparser_name_to_function_dict (dict): A dictionary mapping subparser names to associated functions.
        logger (logging.Logger): The logger object for logging warnings.

    Methods:
        parse_args(): Parse the command-line arguments.
        add_all_subparsers_from_dict(subparser_dict): Add multiple subparsers from a dictionary.
        call_subtool(args): Call the function associated with the selected subtool.

    Example usage:
        parser = MainArgParser(prog='my_tool', description='A command-line tool')
        parser.add_all_subparsers_from_dict({
            Parser1: function1,
            Parser2: function2,
        })
        args = parser.parse_args()
        parser.call_subtool(args)
    """

    def __init__(
        self,
        prog: str,
        subparser_description: str = "",
        subparsers_name: str = "tool",
        description: str = "Select the tool to be used",
        logger: logging.Logger | None = None,
    ):
        # Create an argument parser with the given program name and description
        self.parser = argparse.ArgumentParser(prog=prog, description=description)
        self.subparsers_name = subparsers_name
        # Add subparsers to the argument parser
        self.subparsers = self.parser.add_subparsers(
            title=subparsers_name,
            dest=subparsers_name,
            description=subparser_description,
            required=True,
        )

        self.subparser_name_to_function_dict = dict()
        self.logger = logger or setup_main_logger()

    def parse_args(self):
        return self.parser.parse_args()

    def add_all_subparsers_from_dict(self, subparser_dict):
        """
        Adds all the subparsers from a dictionary to the main parser.

        Parameters:
            subparser_dict (dict): A dictionary containing the subparsers.
            {parser: function}
            - 'parser' (ArgumentParser): The subparser object.
            - 'function' (function): The function associated with the subparser.

        Returns:
            None
        """
        for subparser, function in subparser_dict.items():
            subparser(self.subparsers)
            self.subparser_name_to_function_dict[subparser.name] = function

    def call_subtool(
        self,
        args: argparse.Namespace,
    ):
        if (
            getattr(args, self.subparsers_name)
            in self.subparser_name_to_function_dict.keys()
        ):
            return self.subparser_name_to_function_dict[
                getattr(args, self.subparsers_name)
            ](args)
        else:
            fail_message = (
                f"Invalid tool argument: {getattr(args, self.subparsers_name)}"
            )

            if self.logger is not None:
                self.logger.warning(fail_message)
            else:
                raise ValueError(fail_message)
