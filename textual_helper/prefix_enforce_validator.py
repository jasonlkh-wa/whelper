import textual
from textual.validation import Validator, ValidationResult
from textual.widgets import Input
import re


class PrefixEnforceValidator(Validator):
    """
    The validator is used to memic the behavior of python's [input] funciton
    which allow a text to display before the input from the user
    """

    def __init__(
        self, prefix: str, input_field: Input, suffix_pattern: str | None = None
    ):
        super().__init__()
        self.prefix = prefix
        self.pattern = f"^{re.escape(prefix)}{suffix_pattern or '.*'}$"  # the prefix is always treated as raw text
        self.input_field = input_field

    def is_match(self, value: str):
        return re.match(self.pattern, value)

    def validate(self, value: str) -> ValidationResult:
        if not self.is_match(value):
            failure = self.failure(
                failures=[
                    f"<{value}> does not match pattern: <{self.pattern}>",
                ]
            )
            # revert the last value change
            value_before_last_added_char = value[:-1]
            if self.is_match(value_before_last_added_char):
                self.input_field.value = value_before_last_added_char
            else:
                # The only scenario for a backspace operation to be reverted
                # is when the user backspaces before any new char is added after prefix
                self.input_field.value = self.prefix
            return failure
        return self.success()
