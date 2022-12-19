from returns.result import safe

from dino_seedwork_be.domain.assertion_concern import AssertionConcern

from .exceptions import BusinessRuleValidationException
from .rules import BusinessRule


class BusinessRuleValidationMixin:
    def check_rule(self, rule: BusinessRule):
        if rule.is_broken():
            raise BusinessRuleValidationException(rule)


class OrderItemMixin(AssertionConcern):
    __order: int = 0

    def getOrder(self) -> int:
        return self.__order

    @safe
    def setOrder(self, anIntValue: int):
        self.assertArgumentLargerThan(
            anIntValue, -1, "Order need to a positive number or 0"
        )
        self.__order = anIntValue
        return "OK"
