import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from argparse_helper import MainArgParser, SubtoolParser
import argparse


def create_MainParser():
    return MainArgParser("test")


def create_SubtoolParser(main_parser):
    return SubtoolParser("subparser", "subparser_description")


def create_subparser_dict():
    return {
        "subparser1": {
            "parser": SubtoolParser("subparser1", "show True if dev mode is ON"),
            "function": lambda args: args.dev,
        },
        "subparser2": {
            "parser": SubtoolParser("subparser2", "show True if dev mode is OFF"),
            "function": lambda args: not args.dev,
        },
    }


def create_args_with_subparser1_as_tool():
    return argparse.Namespace(tool="subparser1", dev=True)


def test_MainArgParser():
    parser = create_MainParser()
    assert parser


def test_SubtoolParser():
    main_parser = create_MainParser()
    subparser = create_SubtoolParser(main_parser)

    assert subparser


def test_MainArgParser_add_subparser():
    main_parser = create_MainParser()
    subparser = create_SubtoolParser(main_parser)
    main_parser.add_subparser(subparser)

    assert main_parser


def test_MainArgParser_add_all_subparsers_from_dict():
    main_parser = create_MainParser()
    subparser_dict = create_subparser_dict()
    main_parser.add_all_subparsers_from_dict(subparser_dict)

    assert main_parser.subparser_to_function_dict


def test_MainArgParser_call_subtool():
    main_parser = create_MainParser()
    subparser_dict = create_subparser_dict()
    main_parser.add_all_subparsers_from_dict(subparser_dict)
    args = create_args_with_subparser1_as_tool()
    assert main_parser.call_subtool(args) == True
