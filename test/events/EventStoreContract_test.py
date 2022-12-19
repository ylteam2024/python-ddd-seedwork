from returns.curry import partial
from returns.functions import tap
from returns.pipeline import flow
from returns.pointfree import bind, map_

from dino_seedwork_be.event.EventStore import EventStore
from dino_seedwork_be.utils.functional import (assert_equal,
                                               unwrap_future_result_io)

from .MockEventStore import MockEventStore


class TestEventStoreContract:
    async def test_all_stored_events_between(self):
        event_store = self.event_store()
        await flow(
            event_store.count_events(),
            bind(
                lambda a_number: flow(
                    event_store.all_stored_events_since(0),
                    map_(len),
                    map_(tap(partial(assert_equal, a_number))),
                )
            ),
        ).awaitable()

    async def test_all_stored_events_since(self):
        event_store = self.event_store()
        count_event = unwrap_future_result_io(
            await flow(event_store.count_events()).awaitable()
        )
        await event_store.all_stored_events_since(0).map(len).map(
            tap(partial(assert_equal, count_event))
        ).awaitable()
        await event_store.all_stored_events_since(count_event).map(len).map(
            tap(partial(assert_equal, 0))
        ).awaitable()
        await event_store.all_stored_events_since(count_event - 10).map(len).map(
            tap(partial(assert_equal, 10))
        ).awaitable()

    def event_store(self) -> EventStore:
        event_store = MockEventStore()
        assert event_store is not None
        return event_store
