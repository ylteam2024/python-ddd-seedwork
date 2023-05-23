import json
from typing import Any, List, Tuple, TypeVar

from returns.curry import partial
from returns.future import FutureFailure, FutureResult, FutureSuccess
from returns.iterables import Fold
from returns.pipeline import flow, managed

from dino_seedwork_be.adapters.logger.SimpleLogger import DomainLogger
from dino_seedwork_be.exceptions import MainException
from dino_seedwork_be.utils.process import ThreadLocal

from .DomainEvent import DomainEvent
from .DomainEventSubscriber import DomainEventSubscriber

EventType = TypeVar("EventType", bound=DomainEvent)

# __all__ = ["DomainEventPublisher"]


class DomainEventPublisher:
    ins: ThreadLocal["DomainEventPublisher"]
    _isLock: bool
    _subscribers: List[DomainEventSubscriber]
    logger: DomainLogger = DomainLogger("DomainEventPublisher")

    def __init__(self) -> None:
        self._subscribers = []
        self._isLock = False

    @classmethod
    def instance(cls) -> "DomainEventPublisher":
        try:
            return DomainEventPublisher.ins.value()
        except AttributeError as error:
            cls.logger.info(f"attribute error in publisher {error}")
            DomainEventPublisher.new_instance_for_publisher()
            return DomainEventPublisher.ins.value()

    def is_lock(self) -> bool:
        return self._isLock

    def lock(self):
        self._isLock = True

    def unlock(self):
        self._isLock = False

    def has_subscribers(self) -> bool:
        match len(self._subscribers):
            case 0:
                return False
            case _:
                return True

    def publish(self, an_event: DomainEvent) -> FutureResult[Tuple, Any]:
        def check_if_target_event(event_type: str, subscriber: DomainEventSubscriber):
            match subscriber.event_type_subscribed():
                case list(target_event_types):
                    return event_type in target_event_types
                case str(target_event_type):
                    return target_event_type == event_type or target_event_type == "*"
                case _:
                    return False

        def execute(is_allow_to_run: bool):
            match is_allow_to_run:
                case True:
                    self.lock()
                    return flow(
                        self._subscribers,
                        partial(
                            filter,
                            partial(check_if_target_event, an_event.type()),
                        ),
                        partial(map, lambda sub: sub.handle_event(an_event)),
                        lambda futureS: Fold.collect(futureS, FutureSuccess(())),
                    )
                case False:
                    return FutureFailure(MainException(code="EVENT_PUBLISHER_LOCK"))

        self.logger.info(
            f"Publish domain event {json.dumps(an_event.as_dict())}, {self.is_lock()}, {self.has_subscribers()}",
        )
        return flow(
            FutureSuccess((not self.is_lock()) and self.has_subscribers()),
            managed(execute, lambda *_: FutureResult.from_value(self.unlock())),
        )

    def is_processing(self):
        return self.is_lock()

    def publish_all(self, events: List[DomainEvent]) -> FutureResult[Tuple, Any]:
        return flow(
            events,
            partial(map, lambda event: self.publish(event)),
            lambda futureS: Fold.collect(futureS, FutureSuccess(())),
        )

    def reset(self):
        match self.is_lock():
            case False:
                self.set_subscribers([])

    def set_subscribers(self, subs: List[DomainEventSubscriber]):
        self._subscribers = subs

    def subscribe(self, sub: DomainEventSubscriber):
        match self.is_lock():
            case False:
                self._subscribers.append(sub)

    @staticmethod
    def new_instance_for_publisher():
        DomainEventPublisher.ins = ThreadLocal(
            "domain_publisher", DomainEventPublisher()
        )


# DomainEventPublisher.new_instance_for_publisher()
