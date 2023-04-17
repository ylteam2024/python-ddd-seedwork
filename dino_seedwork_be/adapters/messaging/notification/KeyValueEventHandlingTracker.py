from typing import Any

from returns.future import FutureResult

from dino_seedwork_be.adapters.messaging.notification.EventHandlingTracker import \
    EventHandlingTracker
from dino_seedwork_be.adapters.persistance.key_value.AbstractKeyValueRepository import \
    AbstractKeyValueRepository
from dino_seedwork_be.utils.params import cast_bool_from_str


class KeyValueEventHandlingTracker(EventHandlingTracker):
    _key_value_repository: AbstractKeyValueRepository
    _prefix: str

    def __init__(
        self,
        key_value_repository: AbstractKeyValueRepository,
        prefix: str = "notification_tracker",
    ) -> None:
        self._prefix = prefix
        self._key_value_repository = key_value_repository

    def prefix(self) -> str:
        return self._prefix

    def _key_with_prefix(self, key: str) -> str:
        return f"{self.prefix()}_{key}"

    def check_if_notif_handled(self, a_message_id: str) -> FutureResult[bool, Any]:
        return self._key_value_repository.get(self._key_with_prefix(a_message_id)).map(
            lambda maybe_result: maybe_result.map(cast_bool_from_str).value_or(False)
        )

    def mark_notif_as_handled(self, a_message_id: str) -> FutureResult:
        return self._key_value_repository.set(
            self._key_with_prefix(a_message_id), "True"
        )

    def unmark_notif_as_handled(self, a_message_id: str) -> FutureResult:
        return self._key_value_repository.set(
            self._key_with_prefix(a_message_id), "False"
        )
