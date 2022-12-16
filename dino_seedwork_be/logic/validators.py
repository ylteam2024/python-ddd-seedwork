from typing import Optional

from validators.btc_address import re


def notEmpty(aValue: str, aMessage: Optional[str] = None):
    if aValue.strip() == "":
        raise ValueError(aMessage or "Value cannot be empty")


def testRegex(aValue: str, aRegex: str, aMessage: Optional[str] = None):
    if re.match(aRegex, aValue) is None:
        raise ValueError(aMessage or "Value is not in valid format")
