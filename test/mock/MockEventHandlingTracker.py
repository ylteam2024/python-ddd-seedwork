from typing import Any, Dict

from returns.future import FutureResult, FutureSuccess

from dino_seedwork_be.adapters.messaging.notification.EventHandlingTracker import \
    EventHandlingTracker


class MockEventHandlingTracker(EventHandlingTracker):

    _store: Dict[str, bool]

    def __init__(self) -> None:
        self._store = {}

    def check_if_notif_handled(self, a_message_id: str) -> FutureResult[bool, Any]:
        try:
            return FutureSuccess(self._store[a_message_id])
        except KeyError:
            return FutureSuccess(False)

    def mark_notif_as_handled(self, a_message_id: str) -> FutureResult:
        self._store[a_message_id] = True
        return FutureSuccess(None)
