from dino_seedwork_be.domain.exceptions import (DomainIllegalArgumentException,
                                                DomainIllegalStateException)
from dino_seedwork_be.logic.assertion_concern import AssertionConcern

# __all__ = ["DomainAssertionConcern"]


class DomainAssertionConcern(AssertionConcern):
    IllegalArgExceptionCls = DomainIllegalArgumentException
    IllegalStExceptionCls = DomainIllegalStateException
