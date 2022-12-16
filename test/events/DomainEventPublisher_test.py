from datetime import datetime
from typing import Any, Type

from returns.future import FutureResult, FutureSuccess

from src.seedwork.domain.DomainEventPublisher import DomainEventPublisher
from src.seedwork.domain.DomainEventSubscriber import DomainEventSubscriber
from src.seedwork.utils.functional import returnV, throwException

from .TestableDomainEvent import (AnotherTestableDomainEvent,
                                  TestableDomainEvent)

test_event = TestableDomainEvent(name="test", occurred_on=datetime.now())


class TestDomainEventPublisher:
    event_handled = False
    another_event_handled = False

    class TestDomainEventSubscriber(DomainEventSubscriber[TestableDomainEvent]):
        def handle_event(
            self, an_event: TestableDomainEvent
        ) -> FutureResult[Any, Exception]:
            assert an_event.name() == test_event.name()
            TestDomainEventPublisher.event_handled = True
            return FutureSuccess(None)

        def event_type_subscribed(self) -> Type[TestableDomainEvent]:
            return TestableDomainEvent

    async def test_domain_event_publisher_publish(self):
        DomainEventPublisher.instance().reset()
        DomainEventPublisher.instance().subscribe(self.TestDomainEventSubscriber())
        assert DomainEventPublisher.instance().is_lock() == False
        assert DomainEventPublisher.instance().has_subscribers() == True
        assert TestDomainEventPublisher.event_handled == False

        await DomainEventPublisher.instance().publish(test_event).lash(
            throwException
        ).awaitable()

        assert TestDomainEventPublisher.event_handled == True

    async def test_domain_event_publisher_blocked(self):
        another_test_event = AnotherTestableDomainEvent("TestDomainEvent")
        TestDomainEventPublisher.event_handled = False
        TestDomainEventPublisher.another_event_handled = False

        class TestDomainEventSubscriber(DomainEventSubscriber[TestableDomainEvent]):
            def handle_event(
                self, an_event: TestableDomainEvent
            ) -> FutureResult[Any, Exception]:
                assert an_event.name() == test_event.name()
                TestDomainEventPublisher.event_handled = True
                return (
                    DomainEventPublisher.instance()
                    .publish(another_test_event)
                    .map(returnV("OK"))
                )

            def event_type_subscribed(self) -> Type[TestableDomainEvent]:
                return TestableDomainEvent

        class AnotherTestDomainEventSubscriber(DomainEventSubscriber):
            def handle_event(
                self, an_event: AnotherTestableDomainEvent
            ) -> FutureResult[Any, Exception]:
                TestDomainEventPublisher.another_event_handled = True
                return FutureSuccess(None)

            def event_type_subscribed(self) -> Type[AnotherTestableDomainEvent]:
                return AnotherTestableDomainEvent

        DomainEventPublisher.instance().reset()
        DomainEventPublisher.instance().subscribe(TestDomainEventSubscriber())
        DomainEventPublisher.instance().subscribe(AnotherTestDomainEventSubscriber())

        assert TestDomainEventPublisher.event_handled == False
        assert TestDomainEventPublisher.another_event_handled == False

        await DomainEventPublisher.instance().publish(
            TestableDomainEvent(name="test")
        ).awaitable()

        assert TestDomainEventPublisher.event_handled == True
        assert TestDomainEventPublisher.another_event_handled == False
