from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, List, Optional

from pika.exchange_type import ExchangeType
from returns.functions import tap
from returns.future import FutureResult, FutureSuccess
from returns.maybe import Maybe
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.result import Result, safe

from dino_seedwork_be.adapters.logger.SimpleLogger import DomainLogger
from dino_seedwork_be.adapters.messaging.notification.EventHandlingTracker import \
    EventHandlingTracker
from dino_seedwork_be.utils.functional import feed_args, tap_excute_future

from .ConnectionSettings import ConnectionSettings
from .Exchange import Exchange
from .MessageConsumer import MessageConsumer
from .MessageListener import MessageListener
from .MessageType import MessageType as Type
from .Queue import Queue

# __all__ = ["ExchangeListener"]


class ExchangeListener(ABC):

    _message_consumer: Optional[MessageConsumer]
    _queue: Optional[Queue] = None
    _exchange: Exchange

    is_exchange_durable: bool = True
    is_exchange_auto_delete: bool = False
    exchange_type: ExchangeType = ExchangeType.fanout

    is_queue_durable: bool = True
    is_queue_auto_deleted: bool = False
    is_queue_exclusive: bool = True
    queue_routing_keys: Optional[List[str]] = None

    is_auto_acknowledged: bool = False
    is_retry: bool = False

    label: str = ""
    logger: DomainLogger
    event_handling_tracker: EventHandlingTracker

    def _queue_routing_keys(self) -> List[str]:
        return Maybe.from_optional(self.queue_routing_keys).value_or(self.listen_to())

    def __init__(self, connection_setting: ConnectionSettings) -> None:
        self._connection_setting = connection_setting
        self.attach_to_queue().unwrap()
        self.logger = DomainLogger(self.label)

    def message_consumer(self) -> Maybe[MessageConsumer]:
        return Maybe.from_optional(self._message_consumer)

    @safe
    def close(self):
        """
        " Closes my queues
        """
        self.queue().map(lambda queue: queue.close())

    def queue(self) -> Maybe[Queue]:
        return Maybe.from_optional(self._queue)

    def exchange(self) -> Exchange:
        return self._exchange

    @abstractmethod
    def exchange_name(self) -> str:
        """
        " Answers the String name of the exchange I listen to.
        " @return str
        """
        pass

    @abstractmethod
    def filtered_dispatch(self, a_type: str, a_text_message: str) -> FutureResult:
        ...

    @abstractmethod
    def listen_to(self) -> List[str]:
        """
        " Answers the kinds of messages I listen to.
        " :return: List[str]
        """
        pass

    @abstractmethod
    def queue_name(self) -> str:
        """
        " Answers the str name of the queue I listen to. By
        " default it is the simple name of my concrete class.
        " May be overridden to change the name.
        " :return: str
        """
        pass

    def set_exchange(self, exchange: Exchange):
        self._exchange = exchange

    def set_queue(self, a_queue: Queue):
        self._queue = a_queue

    def attach_to_queue(self) -> Result:

        """
        " Attaches to the queues I listen to for messages.
        """
        return flow(
            [
                self._connection_setting,
                self.exchange_name(),
                self.exchange_type,
                self.is_exchange_durable,
                self.is_exchange_auto_delete,
                lambda exchange: flow(
                    [
                        exchange,
                        self.queue_name(),
                        self._queue_routing_keys(),
                        self.is_queue_durable,
                        self.is_queue_exclusive,
                        self.is_queue_auto_deleted,
                        self.register_consumer,
                    ],
                    feed_args(Queue.factory_exchange_subscriber),
                    map_(tap(self.set_queue)),
                ),
            ],
            feed_args(Exchange.factory),
            map_(tap(self.set_exchange)),
        )

    def set_message_consumer(self, message_consumer: MessageConsumer):
        self._message_consumer = message_consumer

    def itempotent_handle_dispatch(
        self, a_message_id: str, a_type: str, a_binary_message: bytes
    ):
        def idempotent_handle(is_handled: bool):
            match is_handled:
                case False:
                    return self.filtered_dispatch(
                        a_type, a_binary_message.decode()
                    ).bind(
                        tap_excute_future(
                            lambda _: self.event_handling_tracker.mark_notif_as_handled(
                                a_message_id=a_message_id
                            )
                        )
                    )
                case _:
                    return FutureSuccess(None)

        self.logger.info(f"Handle message_id {a_message_id}")
        return self.event_handling_tracker.check_if_notif_handled(a_message_id).bind(
            idempotent_handle
        )

    def register_consumer(self, queue: Queue) -> Result:
        parent = self

        class MessageListenerAdapter(MessageListener):
            def handle_message(
                self,
                a_type: str,
                a_message_id: str,
                a_time_stamp: datetime,
                a_binary_message: bytes,
                a_delivery_tag: int,
                is_redelivery: bool,
            ) -> FutureResult:
                return parent.itempotent_handle_dispatch(
                    a_message_id, a_type, a_binary_message
                )

        rabbitmq_register_consumer: Callable[
            [MessageConsumer], Result
        ] = lambda msg_consumer: msg_consumer.receive_only(
            self.listen_to(), MessageListenerAdapter(Type.TEXT)
        )

        return flow(
            [self.is_auto_acknowledged, queue, self.is_retry, self.label],
            feed_args(MessageConsumer.factory),
            map_(tap(self.set_message_consumer)),
            bind(rabbitmq_register_consumer),
        )

    def is_ready_for_consume(self) -> bool:
        return self.message_consumer().map(lambda ms: ms.is_consuming()).value_or(False)

    def run(self):
        self.exchange().run()

    def stop(self):
        self.message_consumer().map(tap(lambda ms: ms.close()))
