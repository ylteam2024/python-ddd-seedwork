from abc import abstractmethod
from typing import Any

from returns.future import FutureResult
from returns.maybe import Maybe

from dino_seedwork_be.application.ApplicationLifeCycleUseCase import \
    ApplicationLifeCycleUsecase
from dino_seedwork_be.pubsub.NotificationPublisher import NotificationPublisher

__all__ = ["DefaultImplementNotificationApplicationService"]


class DefaultImplementNotificationApplicationService(ApplicationLifeCycleUsecase):

    _notification_publisher: NotificationPublisher

    def __init__(self, notification_publisher: NotificationPublisher) -> None:
        self._notification_publisher = notification_publisher

    def notification_publisher(self) -> NotificationPublisher:
        return self._notification_publisher

    @abstractmethod
    def publish_notifications(self) -> FutureResult:
        ...

    def _publish_notifications(self) -> FutureResult[Maybe[int], Any]:
        """
        publish unpublished event in event store
        :return: return the last event int id that published already
        """
        return self.notification_publisher().publish_notifications()
