import textual
from textual.validation import Validator, ValidationResult
from textual.widgets import Input
import re


class PrefixEnforceValidator(Validator):
    """
    The validator is used to memic the behavior of python's [input] funciton
    which allow a text to display before the input from the user
    """

    def __init__(self, prefix: str, input: Input):
        super().__init__()
        self.prefix = prefix
        self.pattern = f"{prefix}.*"
        self.input = input

    def validate(self, value: str) -> ValidationResult:
        if not re.match(self.pattern, value):
            self.input.value = self.prefix  # revert the value input
            return self.failure(
                failures=[
                    self.prefix,
                    f"{value} does not match pattern: <{self.pattern}>",
                ]
            )
        return self.success()
