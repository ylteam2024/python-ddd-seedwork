from typing import List, Optional

from src.seedwork.exceptions import ExceptionCode, MainException
from src.seedwork.utils.noneOrInstance import noneOrTransform


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
