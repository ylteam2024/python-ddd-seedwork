from abc import ABC, abstractmethod

from returns.future import FutureResult


class UserNotificationPushDrivingAdapter(ABC):
    @abstractmethod
    def push_to_device(
        self, content: dict, type: str, device_token: str
    ) -> FutureResult:
        pass
