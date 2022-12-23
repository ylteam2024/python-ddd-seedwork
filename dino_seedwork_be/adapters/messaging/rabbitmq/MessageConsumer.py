import traceback
from typing import Any, List, Optional, Set

from multimethod import multimethod
from pika import BasicProperties
from pika.amqp_object import Method
from pika.channel import Channel
from returns.curry import partial
from returns.functions import tap
from returns.future import FutureResult, FutureSuccess
from returns.pipeline import flow
from returns.pointfree import alt, bind
from returns.result import Failure, Result, Success, safe

from dino_seedwork_be.adapters import SIMPLE_LOGGER
from dino_seedwork_be.exceptions import MainException
from dino_seedwork_be.utils.functional import (apply, async_execute,
                                               feed_kwargs, return_v,
                                               tap_excute_future)

from .exceptions import MessageException
from .MessageListener import MessageListener
from .Queue import Queue

__all__ = ["MessageConsumer"]


class MessageConsumer:
    _auto_acknowledged: bool

    # My closed property, which indicates I have been closed.
    _closed: bool = False

    _consuming: bool = False

    _is_ready: bool = False

    _is_retry: bool = False

    # My messageTypes, which indicates the messages of types I accept.
    _message_types: Set[str] = set([])

    _prefetch_count: int = 1

    # My queue, which is where my messages come from.
    _queue: Queue

    # My tag, which is produced by the broker.
    _tag: str

    def __init__(
        self,
        a_queue: Queue,
        is_auto_acknowledged: bool,
        is_retry: bool = False,
    ) -> None:
        super().__init__()
        self.set_queue(a_queue)
        self.set_auto_acknowledged(is_auto_acknowledged)
        self.set_message_types(set([]))
        self._is_retry = is_retry

    @multimethod
    @staticmethod
    def factory(a_queue: Queue) -> Result["MessageConsumer", Any]:
        return Success(MessageConsumer(a_queue, False)).bind(
            lambda consumer: consumer.equalize_message_distribution().map(
                return_v(consumer)
            )
        )

    @staticmethod
    @factory.register
    def _(is_auto_acknowledged: bool, a_queue: Queue) -> Result["MessageConsumer", Any]:
        return Success(MessageConsumer(a_queue, is_auto_acknowledged)).bind(
            lambda consumer: consumer.equalize_message_distribution().map(
                return_v(consumer)
            )
        )

    @staticmethod
    @factory.register
    def _(
        is_auto_acknowledged: bool, a_queue: Queue, is_retry: bool
    ) -> Result["MessageConsumer", Any]:
        return Success(MessageConsumer(a_queue, is_auto_acknowledged, is_retry)).bind(
            lambda consumer: consumer.equalize_message_distribution().map(
                return_v(consumer)
            )
        )

    def is_auto_acknowledged(self) -> bool:
        return self._auto_acknowledged

    def set_auto_acknowledged(self, a_bool: bool):
        self._auto_acknowledged = a_bool

    def queue(self) -> Queue:
        return self._queue

    def set_queue(self, a_queue: Queue):
        self._queue = a_queue

    def tag(self) -> str:
        return self._tag

    def is_consuming(self) -> bool:
        return self._consuming

    def is_ready(self) -> bool:
        return self._is_ready

    def is_retry(self) -> bool:
        return self._is_retry

    def set_is_ready(self, a_bool: bool):
        self._is_ready = a_bool

    def set_is_consuming(self, a_bool: bool):
        self._consuming = a_bool

    def set_tag(self, a_tag: str):
        self._tag = a_tag

    def message_types(self) -> Set[str]:
        return self._message_types

    def set_message_types(self, a_message_types: Set[str]):
        self._message_types = a_message_types

    def is_closed(self):
        return self._closed

    def equalize_message_distribution(self) -> Result[None, MessageException]:
        """
        Ensure an equalization of message distribution
        across all consumers of this queue.
        """
        try:
            self.queue().channel().unwrap().basic_qos(
                prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok
            )
            return Success(None)
        except Exception:
            return Failure(MessageException(code="MESSAGE_EQUALIZE_DIS_FAILED"))

    def on_basic_qos_ok(self, _):
        SIMPLE_LOGGER.info("QOS set to: %d", self._prefetch_count)
        self.set_is_ready(True)

    def receive_all(self, a_message_listener: MessageListener) -> Result:
        return self.receive_for(a_message_listener)

    def receive_only(
        self, a_message_types: List[str], a_message_listener: MessageListener
    ) -> Result:
        self.set_message_types(set(a_message_types))
        return self.receive_for(a_message_listener)

    def is_target_message_type(self, message_type: Optional[str]) -> bool:
        match len(self.message_types()):
            case 0:
                return True
            case _:
                is_filterred_out = (
                    message_type is None or message_type not in self.message_types()
                )
                return not is_filterred_out

    def receive_for(self, a_message_listener: MessageListener) -> Result:
        queue = self.queue()
        channel = queue.channel().unwrap()

        def ack(
            channel: Channel,
            delivery_tag: int,
        ):
            try:
                match self.is_auto_acknowledged():
                    case False:
                        channel.basic_ack(delivery_tag, False)
                        SIMPLE_LOGGER.info(
                            f"ACK handle message success {self.message_types()}",
                        )
                return FutureSuccess(None)
            except Exception as error:
                SIMPLE_LOGGER.error("Exception on ACK %s", error)
                raise error

        def nak(channel: Channel, delivery_tag: int, is_retry: bool):
            try:
                match self.is_auto_acknowledged():
                    case False:
                        SIMPLE_LOGGER.info(
                            "NonACK handle message failed, would retry ? %s", is_retry
                        )
                        channel.basic_nack(delivery_tag, False, is_retry)
            except Exception as error:
                raise error

        def handle_delivery_exception(
            channel: Channel, delivery_tag: int, is_retry: bool, exception: Exception
        ):
            SIMPLE_LOGGER.info("Exception on handle delivery %s", exception)
            traceback.print_exc()
            match exception:
                case MessageException():
                    nak(channel, delivery_tag, is_retry)
                case _:
                    nak(channel, delivery_tag, False)
            # do not shutdown
            # raise exception

        def handle_delivery(
            channel: Channel, method: Method, properties: BasicProperties, body: bytes
        ) -> FutureResult:
            match self.is_target_message_type(properties.type):
                case True:
                    SIMPLE_LOGGER.info("Handle delivery %s", properties.type)
                    return flow(
                        {
                            "a_type": properties.type,
                            "a_message_id": properties.message_id,
                            "a_time_stamp": properties.timestamp,
                            "a_binary_message": body,
                            "a_delivery_tag": getattr(method, "delivery_tag", 0),
                            "is_redelivery": getattr(method, "delivered", False),
                        },
                        feed_kwargs(a_message_listener.handle_message),
                        bind(
                            tap_excute_future(
                                apply(ack, channel, getattr(method, "delivery_tag", 0))
                            )
                        ),
                        alt(
                            tap(
                                partial(
                                    handle_delivery_exception,
                                    channel,
                                    getattr(method, "delivery_tag", 0),
                                    self.is_retry(),
                                )
                            )
                        ),
                    )
                case False:
                    return ack(channel, getattr(method, "delivery_tag", 0)).bind(
                        return_v(FutureSuccess("NOT_TARGET_MESSAGE"))
                    )

        try:
            tag = channel.basic_consume(
                queue.name(),
                auto_ack=self.is_auto_acknowledged(),
                on_message_callback=async_execute(handle_delivery),
            )
            channel.add_on_cancel_callback(self.on_consumer_cancelled)
            SIMPLE_LOGGER.info("Register message listener success")
            self.set_tag(tag)
            self.set_is_consuming(True)
            return Success(None)
        except Exception:
            return Failure(MainException(code="INITIATE_CONSUMER_FAILED"))

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.
        :param pika.frame.Method method_frame: The Basic.Cancel frame
        """
        SIMPLE_LOGGER.info(
            "Consumer was cancelled remotely, shutting down: %r", method_frame
        )
        self.close_channel()

    @safe
    def close_channel(self):
        self.queue().channel().map(lambda channel: channel.close())

    def _stop_consuming(self):
        def _cb():
            self.queue.close()

        self.queue().channel().map(
            lambda channel: channel.basic_cancel(self.tag(), _cb)
        )

    @safe
    def close(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.
        """
        self._closed = True
        match self.is_consuming():
            case True:
                self._stop_consuming()
            case False:
                self.queue().close()

    def run(self):
        self.queue().run()
