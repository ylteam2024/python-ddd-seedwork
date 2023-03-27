from abc import ABC, abstractmethod
from typing import Any

from returns.future import FutureResult
from returns.maybe import Maybe
from returns.result import Result

from dino_seedwork_be.storage.uow import DBSessionUser

__all__ = ["NotificationPublisher"]


class NotificationPublisher(ABC, DBSessionUser):
    @abstractmethod
    def publish_notifications(self) -> FutureResult[Maybe[int], Any]:
        """
        publish unpublished event in event store
        :return: return the last event int id that published already
        """
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def is_ready(self) -> Result[bool, Any]:
        pass

    @abstractmethod
    def get_last_published_notification_id(self) -> FutureResult[Maybe[int], Any]:
        ...

    # @abstractmethod
    # def internal_only_test_confirmation():
    #     pass
