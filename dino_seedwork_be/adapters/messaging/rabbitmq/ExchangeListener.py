from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from returns.functions import tap
from returns.future import FutureResult
from returns.maybe import Maybe
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.result import Result, safe

from dino_seedwork_be.utils.functional import feed_args

from .ConnectionSettings import ConnectionSettings
from .Exchange import Exchange
from .MessageConsumer import MessageConsumer
from .MessageListener import MessageListener
from .MessageType import MessageType as Type
from .Queue import Queue

__all__ = ["ExchangeListener"]


class ExchangeListener(ABC):
    _message_consumer: Optional[MessageConsumer]
    _queue: Optional[Queue] = None
    _exchange: Exchange
    is_durable: bool = True
    is_queue_durable: bool = True
    is_queue_auto_deleted: bool = False
    is_auto_acknowledged: bool = False
    is_retry: bool = False
    is_exclusive: bool = True

    def __init__(
        self,
        broker_host: str,
        broker_port: int,
        broker_virtual_host: str,
        broker_user_name: Maybe[str],
        broker_user_password: Maybe[str],
    ) -> None:
        self.attach_to_queue(
            broker_host,
            broker_port,
            broker_virtual_host,
            broker_user_name,
            broker_user_password,
        )

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

    def attach_to_queue(
        self,
        broker_host: str,
        broker_port: int,
        broker_virtual_host: str,
        broker_user_name: Maybe[str],
        broker_user_password: Maybe[str],
    ) -> Result:

        """
        " Attaches to the queues I listen to for messages.
        """
        return flow(
            [
                ConnectionSettings.factory(
                    broker_host,
                    broker_port,
                    broker_virtual_host,
                    broker_user_name.value_or(None),
                    broker_user_password.value_or(None),
                ),
                self.exchange_name(),
                self.is_durable,
                lambda exchange: flow(
                    [
                        exchange,
                        self.queue_name(),
                        self.register_consumer,
                        self.is_queue_durable,
                        self.is_queue_auto_deleted,
                        self.is_exclusive,
                    ],
                    feed_args(Queue.factory_exchange_subscriber),
                    map_(tap(self.set_queue)),
                ),
            ],
            feed_args(Exchange.fanout_instance),
            map_(tap(self.set_exchange)),
        )

    def set_message_consumer(self, message_consumer: MessageConsumer):
        self._message_consumer = message_consumer

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
                return parent.filtered_dispatch(a_type, a_binary_message.decode())

        return flow(
            [self.is_auto_acknowledged, queue, self.is_retry],
            feed_args(MessageConsumer.factory),
            map_(tap(self.set_message_consumer)),
            bind(
                lambda msg_consumer: msg_consumer.receive_only(
                    self.listen_to(), MessageListenerAdapter(Type.TEXT)
                )
            ),
        )

    def is_ready_for_consume(self) -> bool:
        return self.message_consumer().map(lambda ms: ms.is_consuming()).value_or(False)

    def run(self):
        self.exchange().run()

    def stop(self):
        self.message_consumer().map(tap(lambda ms: ms.close()))
