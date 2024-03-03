import argparse
from whelper import printls


def raisels_in_arg(error: Exception, message: str):
    """Force printing a message when argparser's argument validation failed.
    This function is used to force printing a message as argparser's argument validation
    will suppress regular error message raised."""
    printls(message)
    raise error
