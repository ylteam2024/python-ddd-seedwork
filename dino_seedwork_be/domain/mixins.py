from returns.maybe import Some
from returns.result import safe

from dino_seedwork_be.logic import AssertionConcern

# __all__ = ["OrderItemMixin"]


class OrderItemMixin(AssertionConcern):
    _order: int = 0

    def get_order(self) -> int:
        return self._order

    @safe
    def set_order(self, order: int):
        self.assert_argument_larger_than(
            order, -1, Some("Order need to a positive number or 0")
        ).unwrap()
        self._order = order
        return "OK"
