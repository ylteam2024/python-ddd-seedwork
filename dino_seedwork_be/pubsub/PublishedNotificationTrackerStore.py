from abc import abstractmethod
from typing import Any, List

from returns.future import FutureResult
from returns.maybe import Maybe

from src.seedwork.adapters.repository import Repository
from src.seedwork.pubsub.Notification import Notification
from src.seedwork.pubsub.PublishedNotificationTracker import \
    PublishedNotificationTracker
from src.seedwork.storage.uow import DBSessionUser


class PublishedNotificationTrackerStore(DBSessionUser):
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
