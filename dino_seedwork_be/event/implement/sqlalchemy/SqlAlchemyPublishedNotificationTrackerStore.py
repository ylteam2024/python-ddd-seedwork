from typing import List, Type

from returns.future import future_safe
from returns.maybe import Maybe, Nothing, Some
from sqlalchemy import Column, Integer, String, select, update

from dino_seedwork_be.pubsub import (Notification,
                                     PublishedNotificationTracker,
                                     PublishedNotificationTrackerStore)
from dino_seedwork_be.storage.alchemysql import AlchemyRepository

__all__ = [
    "SqlAlchemyBasePublishedNotifTracker",
    "SqlAlchemyPublishedNotificationTrackerStore",
]


class SqlAlchemyBasePublishedNotifTracker:
    last_published_event_id = Column(Integer())
    type_name = Column(String(), primary_key=True, nullable=False)


class SqlAlchemyPublishedNotificationTrackerStore(
    PublishedNotificationTrackerStore, AlchemyRepository
):
    _db_model: Type[SqlAlchemyBasePublishedNotifTracker]
    _type_name: str

    def __init__(
        self,
        db_model: Type[SqlAlchemyBasePublishedNotifTracker],
        type_name: str,
    ) -> None:
        self._db_model = db_model
        self._type_name = type_name
        super().__init__()

    @future_safe
    async def published_notification_tracker(self) -> PublishedNotificationTracker:
        stmt = select(self.db_model()).where(
            self.db_model().type_name == self.type_name()
        )
        tracker = (await self.session().execute(stmt)).scalars().first()
        match tracker:
            case None:
                new_tracker = PublishedNotificationTracker.factory(
                    type_name=self._type_name
                ).unwrap()
                self.session().add(self.db_model()(type_name=self._type_name))
                return new_tracker
            case _:
                return PublishedNotificationTracker.factory(
                    type_name=self.type_name(),
                    most_recent_published_notification_id=tracker.last_published_event_id,
                ).unwrap()

    @future_safe
    async def track_most_recent_published_notification(
        self, a_tracker: PublishedNotificationTracker, notifications: List[Notification]
    ) -> Maybe[int]:
        match len(notifications):
            case 0:
                return Nothing
            case _:
                last_notfi = notifications[-1]
                a_tracker.set_most_recent_published_notification_id(last_notfi.id())
                last_published_notif_id = (
                    a_tracker.most_recent_published_notification_id().value_or(None)
                )
                match last_published_notif_id:
                    case int(an_id):
                        stmt = (
                            update(self.db_model())
                            .where(self.db_model().type_name == a_tracker.type_name())
                            .values(last_published_event_id=an_id)
                        )
                        await self.session().execute(stmt)
                await self.session().commit()
                return Some(last_notfi.id())

    def db_model(self) -> Type[SqlAlchemyBasePublishedNotifTracker]:
        return self._db_model

    def type_name(self) -> str:
        return self._type_name
