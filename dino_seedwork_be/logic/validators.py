from typing import Optional

from validators.btc_address import re

__all__ = ["not_empty", "test_regex"]


def not_empty(a_value: str, a_message: Optional[str] = None):
    if a_value.strip() == "":
        raise ValueError(a_message or "Value cannot be empty")


def test_regex(a_value: str, a_regex: str, a_message: Optional[str] = None):
    if re.match(a_regex, a_value) is None:
        raise ValueError(a_message or "Value is not in valid format")
