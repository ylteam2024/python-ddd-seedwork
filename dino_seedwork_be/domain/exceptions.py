from typing import List, Optional

from dino_seedwork_be.exceptions import MainException

__all__ = [
    "DomainException",
    "BusinessRuleValidationException",
    "DomainIllegalStateException",
    "DomainIllegalArgumentException",
]


class DomainException(MainException):
    pass


class BusinessRuleValidationException(DomainException):
    pass


class DomainIllegalArgumentException(BusinessRuleValidationException):
    def __init__(
        self,
        message: str,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ):
        super().__init__(
            message=f"IllegalArgumentException in Domain Logic: {message}",
            loc=loc,
            code=code,
        )


class DomainIllegalStateException(BusinessRuleValidationException):
    def __init__(
        self,
        message: str,
        loc: Optional[List[str]] = None,
        code: Optional[str] = None,
    ):
        super().__init__(
            message=f"IllegalStateException in Domain Logic: {message}",
            loc=loc,
            code=code,
        )
