from datetime import datetime
from typing import Any, List, Type

from returns.curry import partial
from returns.functions import tap
from returns.future import FutureResult, FutureSuccess, future_safe
from returns.pipeline import flow
from returns.pointfree import alt, bind, map_
from sqlalchemy import Column, DateTime, Integer, String, select
from sqlalchemy.sql.functions import count

from dino_seedwork_be.domain.DomainEvent import DomainEvent
from dino_seedwork_be.event.EventSerializer import EventSerializer
from dino_seedwork_be.event.EventStore import EventStore
from dino_seedwork_be.event.StoredEvent import StoredEvent
from dino_seedwork_be.storage.uow import DBSessionUser
from dino_seedwork_be.utils import (async_to_future_result, feed_kwargs,
                                    print_result_with_text, return_v)

__all__ = ["SqlAlchemyBaseEvent", "SqlAlchemyEventStore"]


class SqlAlchemyBaseEvent:
    __tablename__ = "event_store"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    occurred_on = Column(DateTime(timezone=True), default=datetime.now())
    body = Column(String())
    type_name = Column(String(), nullable=False)


class SqlAlchemyEventStore(EventStore, DBSessionUser):
    _db_model: Type[SqlAlchemyBaseEvent]

    def __init__(self, db_model: Type[SqlAlchemyBaseEvent]) -> None:
        self._db_model = db_model

    @future_safe
    async def all_stored_events_since(self, an_event_id: int) -> List[StoredEvent]:
        stmt = select(self._db_model).where(self._db_model.id > an_event_id)
        result = (await self.session().execute(stmt)).scalars().all()
        return flow(
            result,
            partial(
                map,
                lambda r: StoredEvent(
                    id=r.id,
                    occurred_on=r.occurred_on,
                    type_name=r.type_name,
                    body=r.body,
                ),
            ),
            list,
        )

    def all_stored_events_between(
        self, a_low_stored_event_id: int, a_high_stored_event_id: int
    ) -> FutureResult[List[StoredEvent], Any]:
        return FutureSuccess([])

    def append(self, an_domain_event: DomainEvent) -> FutureResult[StoredEvent, Any]:
        stored_event_result = flow(
            an_domain_event,
            EventSerializer.instance().serialize,
            map_(
                lambda body: {
                    "body": body,
                    "occurred_on": an_domain_event.occurred_on(),
                    "type_name": an_domain_event.type(),
                }
            ),
            map_(feed_kwargs(StoredEvent)),
        )
        return flow(
            stored_event_result.map(
                lambda v: {
                    "occurred_on": v.occurred_on(),
                    "type_name": v.type_name(),
                    "body": v.body(),
                }
            ),
            map_(feed_kwargs(self._db_model)),
            map_(tap(self.session().add)),
            bind(lambda _: async_to_future_result(self.session().commit)()),
            map_(print_result_with_text("Commit event to event store")),
            bind(return_v(FutureResult.from_result(stored_event_result))),
            alt(tap(lambda _: async_to_future_result(self.session().rollback)())),
        )

    def close(self):
        ...

    @future_safe
    async def count_events(self) -> int:
        stmt = select(count(self._db_model.id))
        return (await self.session().execute(stmt)).scalar()
