from typing import Any

from returns.maybe import Some
from returns.result import Result

from dino_seedwork_be.domain.value_object.AbstractIdentity import \
    AbstractIdentity

# __all__ = ["NID"]


class NID(AbstractIdentity[int]):
    def validate(self, an_id: int) -> Result[int, Any]:
        return self.assert_argument_larger_than(
            an_id, 0, code=Some("NUMBER_ID_SHOULD_>_0")
        )
