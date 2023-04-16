from returns.result import safe

from dino_seedwork_be.logic import AssertionConcern

__all__ = ["OrderItemMixin"]


class OrderItemMixin(AssertionConcern):
    __order: int = 0

    def getOrder(self) -> int:
        return self.__order

    @safe
    def setOrder(self, anIntValue: int):
        self.assert_argument_larger_than(
            anIntValue, -1, "Order need to a positive number or 0"
        ).unwrap()
        self.__order = anIntValue
        return "OK"
