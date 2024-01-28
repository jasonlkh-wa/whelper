import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import prefix_enforce_validator


def create_prefix_validator_without_suffix_pattern():
    return prefix_enforce_validator.PrefixEnforceValidator(
        prefix="test: ", input_field=None
    )


def create_prefix_validator_with_suffix_pattern():
    return prefix_enforce_validator.PrefixEnforceValidator(
        prefix="test: ", input_field=None, suffix_pattern="[yn]{1}"
    )


def test_is_match_without_suffix_validator():
    validator = create_prefix_validator_without_suffix_pattern()
    assert validator.is_match("test: ")
    assert not validator.is_match("test:")  # remove 1 char


def test_is_match_with_suffix_validator():
    validator = create_prefix_validator_with_suffix_pattern()
    assert not validator.is_match("test:")  # remove 1 char
    assert validator.is_match("test: y")
    assert validator.is_match("test: n")
    assert not validator.is_match("test: a")  # add 1 invalid char
    assert not validator.is_match("test: yy")  # add 1 extra invalid char
