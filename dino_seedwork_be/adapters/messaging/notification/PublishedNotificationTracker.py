from typing import Any, Optional

from returns.maybe import Maybe
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.result import Failure, Result, Success

from dino_seedwork_be.logic.assertion_concern import AssertionConcern
from dino_seedwork_be.utils.functional import apply, return_v

__all__ = ["PublishedNotificationTracker"]


class PublishedNotificationTracker(AssertionConcern):
    _concurrency_version: int = 0
    _most_recent_published_notification_id: Optional[int] = None
    _id: Optional[int]
    _type_name: str

    def __init__(self):
        super().__init__()

    @staticmethod
    def factory(
        type_name: str,
        id: Optional[int] = None,
        most_recent_published_notification_id: Optional[int] = None,
    ) -> Result["PublishedNotificationTracker", Any]:
        tracker = PublishedNotificationTracker()
        return flow(
            tracker.set_type_name(type_name),
            map_(apply(tracker.set_id, id)),
            bind(
                apply(
                    tracker.set_most_recent_published_notification_id,
                    most_recent_published_notification_id,
                )
            ),
            map_(return_v(tracker)),
        )

    def concurrency_version(self) -> int:
        return self._concurrency_version

    def id(self) -> Maybe[int]:
        return Maybe.from_optional(self._id)

    def type_name(self) -> str:
        return self._type_name

    def most_recent_published_notification_id(self) -> Maybe[int]:
        return Maybe.from_optional(self._most_recent_published_notification_id)

    def set_most_recent_published_notification_id(
        self, an_num_id: int | None
    ) -> Result[None, Any]:
        match an_num_id:
            case int():
                assert_result = self.assert_argument_larger_than(
                    an_num_id, 0, "notification id must be large than zero"
                )
                match assert_result:
                    case Failure(_):
                        return assert_result
                    case _:
                        self._most_recent_published_notification_id = an_num_id
                        return Success(None)
        return Success(None)

    def set_type_name(self, an_type_name: str) -> Result[None, Any]:
        assert_condition = flow(
            self.assert_argument_not_empty(
                an_type_name,
                code="TRACKER_type_name_NOT_EMPTY",
                a_message="The tracker topic name is required",
            ),
            bind(
                lambda _: self.assert_argument_length(
                    an_type_name,
                    1,
                    100,
                    "The tracker topic name must be 100 characters or less",
                )
            ),
        )
        match assert_condition:
            case Success(_):
                self._type_name = an_type_name
                return Success(None)
            case _:
                return assert_condition

    def set_id(self, an_id: int):
        self._id = an_id

    def set_concurrency_version(self, version: int):
        self._concurrency_version = version
