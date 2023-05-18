from abc import abstractmethod
from typing import Any, List

from firebase_admin.messaging import Notification
from returns.future import FutureResult
from returns.maybe import Maybe

from dino_seedwork_be.adapters.messaging.notification.PublishedNotificationTracker import \
    PublishedNotificationTracker

__all__ = ["PublishedNotificationTrackerStore"]


class PublishedNotificationTrackerStore:
    @abstractmethod
    def published_notification_tracker() -> FutureResult[
        PublishedNotificationTracker, Exception
    ]:
        ...

    @abstractmethod
    def track_most_recent_published_notification(
        self, a_tracker: PublishedNotificationTracker, notifications: List[Notification]
    ) -> FutureResult[Maybe[int], Any]:

        """
        persisting last event identifier that published in tracker
        :param a_tracker: tracker
        :notifications: List of published event as notifications
        :return: return the last event int id that published already
        """
        pass

    @abstractmethod
    def topic_name() -> str:
        ...
