from random import randrange
from test.events.TestableDomainEvent import TestableDomainEvent
from typing import Any, List, cast

from returns.curry import partial
from returns.functions import tap
from returns.future import FutureResult, FutureSuccess
from returns.iterables import Fold
from returns.maybe import Some
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.result import Success

from dino_seedwork_be.domain.DomainEvent import DomainEvent
from dino_seedwork_be.domain.event.EventSerializer import EventSerializer
from dino_seedwork_be.domain.event.EventStore import EventStore
from dino_seedwork_be.domain.event.StoredEvent import StoredEvent
from dino_seedwork_be.utils.functional import feed_kwargs, for_each
from dino_seedwork_be.utils.meta import get_class_name


class MockEventStore(EventStore):
    _START_ID = 789

    _stored_events: List[StoredEvent]

    def __init__(self) -> None:
        self._stored_events = []

        number_of_stored_events = randrange(1, 1001)

        match number_of_stored_events < 21:
            case True:
                number_of_stored_events = 21
        flow(
            map(
                lambda idx: self._new_stored_event(
                    MockEventStore._START_ID + idx, idx + 1
                ),
                range(0, number_of_stored_events),
            ),
            lambda future_stored_events: Fold.collect(
                future_stored_events, Success(())
            ),
            map_(
                tap(
                    partial(
                        for_each,
                        lambda stored_event, _: self._stored_events.append(
                            stored_event
                        ),
                    )
                )
            ),
        )

    def all_stored_events_between(
        self, a_low_stored_event_id: int, a_high_stored_event_id: int
    ) -> FutureResult[List[StoredEvent], Any]:
        return FutureSuccess(
            list(
                filter(
                    lambda stored_event: stored_event.id().value_or(0)
                    >= a_low_stored_event_id
                    and stored_event.id().value_or(0) <= a_high_stored_event_id,
                    self._stored_events,
                )
            )
        )

    def all_stored_events_since(
        self, a_stored_event_id: int
    ) -> FutureResult[List[StoredEvent], Exception]:
        return FutureSuccess(
            list(
                filter(
                    lambda stored_event: stored_event.id().value_or(0)
                    > a_stored_event_id,
                    self._stored_events,
                )
            )
        )

    def append(
        self, a_domain_event: DomainEvent
    ) -> FutureResult[StoredEvent, Exception]:
        return flow(
            a_domain_event,
            EventSerializer.instance().serialize,
            map_(
                lambda serialized_event: {
                    "type_name": get_class_name(a_domain_event),
                    "occurred_on": a_domain_event.occurred_on(),
                    "body": serialized_event,
                }
            ),
            map_(feed_kwargs(StoredEvent.factory)),
            bind(
                lambda stored_event: self.count_events()
                .map(lambda count: cast(StoredEvent, stored_event).set_id(count + 1))
                .map(tap(lambda _: self._stored_events.append(stored_event)))
            ),
        )

    def count_events(self) -> FutureResult[int, Any]:
        return FutureSuccess(len(self._stored_events))

    def _new_stored_event(self, domain_event_id: int, stored_event_id: int):
        serializer = EventSerializer.instance()
        event = TestableDomainEvent("name " + str(domain_event_id))
        return flow(
            event,
            serializer.serialize,
            map_(
                lambda s_event: StoredEvent(
                    type_name=get_class_name(event),
                    occurred_on=event.occurred_on(),
                    id=Some(stored_event_id),
                    body=str(s_event),
                )
            ),
        )

    def close(self):
        pass
