from abc import abstractmethod
from typing import Any

from returns.future import FutureResult


class EventHandlingTracker:
    @abstractmethod
    def check_if_notif_handled(self, a_message_id: str) -> FutureResult[bool, Any]:
        pass

    @abstractmethod
    def mark_notif_as_handled(self, a_message_id: str) -> FutureResult:
        pass
