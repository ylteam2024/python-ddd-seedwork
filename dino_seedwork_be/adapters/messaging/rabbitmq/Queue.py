import logging
from typing import Any, Callable, List, Optional, Union

from multimethod import multimethod
from returns.curry import partial
from returns.iterables import Fold
from returns.maybe import Maybe
from returns.result import Failure, Result, Success, safe

from dino_seedwork_be.adapters import SIMPLE_LOGGER
from dino_seedwork_be.exceptions import MainException
from dino_seedwork_be.utils import execute, unsafe_panic

from .BrokerComponent import BrokerComponent
from .ConnectionSettings import ConnectionSettings
from .Exchange import Exchange

LOGGER = logging.getLogger(__name__)

__all__ = ["Queue"]


class Queue(BrokerComponent):

    _is_auto_deleted: bool
    _is_exclusive: bool
    _is_queue_ready: bool = False

    def is_queue(self) -> bool:
        return True

    @multimethod
    def __init__(
        self,
        a_con_settings: ConnectionSettings,
        a_name: str,
        is_durable: bool,
        is_exclusive: bool,
        is_auto_deleted: bool,
        on_setup_finish: Optional[Callable[[Any], Any]],
    ):
        """
        Constructs my default state.
        @param a_con_settings the ConnectionSettings to initialize with
        @param a_name the String name of the queue, or the empty string
        @param is_durable the boolean indicating whether or not I am durable
        @param is_exclusive the boolean indicating whether or not I am exclusive
        @param is_auto_deleted the boolean indicating whether or not I should be auto-deleted
        """

        super().__init__(a_con_settings=a_con_settings, on_setup_finish=on_setup_finish)
        self.set_durable(is_durable)
        self.set_name(a_name)
        self._is_exclusive = is_exclusive
        self._is_auto_deleted = is_auto_deleted

    @__init__.register
    def _(
        self,
        a_broker_channel: Union[Exchange, "Queue"],
        a_name: str,
        is_durable: bool,
        is_exclusive: bool,
        is_auto_deleted: bool,
        on_setup_finish: Optional[Callable[[Any], Any]],
    ):
        """
        Constructs my default state.
        @param a_broker_channel the BrokerChannel to initialize with
        @param a_name the String name of the queue, or the empty string
        @param is_durable the boolean indicating whether or not I am durable
        @param is_exclusive the boolean indicating whether or not I am exclusive
        @param is_auto_deleted the boolean indicating whether or not I should be auto-deleted
        """

        self.set_durable(is_durable)
        self.set_name(a_name)
        self._is_exclusive = is_exclusive
        self._is_auto_deleted = is_auto_deleted
        super().__init__(a_broker_channel, on_setup_finish)

    @multimethod
    @staticmethod
    @safe
    def factory(
        a_con_settings: ConnectionSettings,
        a_name: str,
        on_setup_finish: Optional[Callable[[Any], Any]],
    ):
        """
        Answers a new instance of a Queue with the name a_name. The underlying
        queue is non-durable, non-exclusive, and not auto-deleted.
        @param a_connection_settings the ConnectionSettings
        @param a_name the String name of the queue
        @return Queue
        """
        return Queue(
            a_con_settings, a_name, False, False, False, on_setup_finish=on_setup_finish
        )

    @safe
    @factory.register
    @staticmethod
    def _(
        a_con_settings: ConnectionSettings,
        a_name: str,
        is_durable: bool,
        is_exclusive: bool,
        is_auto_deleted: bool,
        on_setup_finish: Optional[Callable[[Any], Any]],
    ) -> "Queue":
        """
        Answers a new instance of a Queue with the name a_name. The underlying
        queue durability, exclusivity, and deletion properties are specified by
        explicit parameters.
        @param a_connection_settings the ConnectionSettings
        @param a_name the String name of the queue
        @param is_durable the boolean indicating whether or not I am durable
        @param is_exclusive the boolean indicating whether or not I am exclusive
        @param is_auto_deleted the boolean indicating whether or not I should be auto-deleted
        @return Queue
        """
        return Queue(
            a_con_settings,
            a_name,
            is_durable,
            is_exclusive,
            is_auto_deleted,
            on_setup_finish,
        )

    @staticmethod
    @safe
    def factory_durable_instance(
        a_connection_settings: ConnectionSettings,
        a_name: str,
        on_setup_finish: Optional[Callable[[Any], Any]],
    ) -> "Queue":
        """
        Answers a new instance of a Queue with the name a_name. The underlying
        queue is durable, exclusive, and not auto-deleted.
        @param a_connection_settings the ConnectionSettings
        @param a_name the String name of the queue
        @return Queue
        """

        return Queue(
            a_connection_settings,
            a_name,
            True,
            False,
            False,
            on_setup_finish,
        )

    @staticmethod
    @safe
    def factory_durable_exclusive_instance(
        a_connection_settings: ConnectionSettings,
        a_name: str,
        on_setup_finish: Optional[Callable],
    ) -> "Queue":
        """
        * Answers a new instance of a Queue with the name aName. The underlying
        * queue is durable, exclusive, and not auto-deleted.
        * @param a_connection_settings the ConnectionSettings
        * @param a_name the String name of the queue
        * @return Queue
        """
        return Queue(
            a_connection_settings,
            a_name,
            True,
            True,
            False,
            on_setup_finish,
        )

    @multimethod
    @staticmethod
    @safe
    def factory_exchange_subscriber(
        an_exchange: Exchange,
        a_name: str,
        cb: Optional[Callable[[Any], Result]] = None,
        is_durable: bool = False,
        is_auto_deleted: bool = True,
        is_exclusive: bool = True,
    ):
        SIMPLE_LOGGER.info(
            "Factory a QUEUE is durable %s, is_auto_deleted %s, is_exclusive %s"
            % (is_durable, is_auto_deleted, is_exclusive)
        )

        def callback(_):
            return Queue._bind_queue(queue, an_exchange, cb, "")

        queue = Queue(
            an_exchange,
            a_name or "",
            is_durable,
            is_exclusive,
            is_auto_deleted,
            callback,
        )
        return queue

    @staticmethod
    @factory_exchange_subscriber.register
    def _(
        an_exchange: Exchange,
        routing_keys: List[str],
        cb: Optional[Callable] = None,
        is_durable: bool = False,
        is_auto_deleted: bool = True,
        is_exclusive: bool = True,
    ):
        """
        Answers a new instance of a Queue that is bound to an_exchange, and
        is ready to participate as an exchange subscriber (pub/sub). The
        connection and channel of an_exchange are reused. The Queue is
        uniquely named by the server, non-durable, exclusive, and auto-deleted.
        The queue is bound to all routing keys in routing_keys. This Queue
        style best works as a temporary direct or topic subscriber.
        @param an_exchange the Exchange to bind with the new Queue
        @return Queue
        """

        def callback(_):
            return Fold.collect(
                map(partial(Queue._bind_queue, queue, an_exchange, cb), routing_keys),
                Result(()),
            ).unwrap()

        queue = Queue(
            an_exchange,
            "",
            is_durable,
            is_exclusive,
            is_auto_deleted,
            callback,
        )
        return queue

    @staticmethod
    @factory_exchange_subscriber.register
    def _(
        an_exchange: Exchange,
        a_name: str,
        routing_keys: List[str],
        is_durable: bool,
        is_exclusive: bool,
        is_auto_deleted: bool,
        cb: Optional[Callable[[Any], Result]],
    ) -> "Queue":
        """
        Answers a new instance of a Queue that is bound to an_exchange, and
        is ready to participate as an exchange subscriber (pub/sub). The
        connection and channel of an_exchange are reused. The Queue is named
        by aName, unless it is empty, in which case the name is generated by
        the broker. The Queue is bound to all routing keys in routing_keys,
        or to no routing key if aRoutingKeys is empty. The Queue has the
        qualities specified by is_durable, is_exclusive, is_auto_deleted. This
        factory is provided for ultimate flexibility in case no other
        exchange-queue binder factories fit the needs of the client.
        @param an_exchange the Exchange to bind with the new Queue
        @param a_name the String name of the queue
        @param routing_keys the routing keys to bind the queue to
        @param is_durable the boolean indicating whether or not I am durable
        @param is_exclusive the boolean indicating whether or not I am exclusive
        @param is_auto_deleted the boolean indicating whether or not I should be auto-deleted
        @return Queue
        """

        def callback(_):
            match len(routing_keys):
                case 0:
                    return Queue._bind_queue(queue, an_exchange, cb, "")
                case _:
                    return Fold.collect(
                        map(
                            partial(Queue._bind_queue, queue, an_exchange, cb),
                            routing_keys,
                        ),
                        Result(()),
                    ) or Result(None)

        queue = Queue(
            an_exchange,
            a_name,
            is_durable,
            is_exclusive,
            is_auto_deleted,
            on_setup_finish=callback,
        )
        return queue

    @staticmethod
    def _bind_queue(
        a_queue: "Queue",
        an_exchange: Exchange,
        cb: Optional[Callable[[Any], Result]],
        routing_key: str,
    ) -> Result:
        def on_bind_ok(_):
            LOGGER.info("Queue bind successfully")
            execute_result = execute(cb, a_queue)
            Maybe.from_optional(execute_result).map(lambda r: r.unwrap())
            a_queue.set_queue_ready_status(True)

        try:
            a_queue.channel().unwrap().queue_bind(
                a_queue.name(), an_exchange.name(), routing_key, callback=on_bind_ok
            )
            return Success(None)
        except Exception as error:
            return Failure(
                MainException(code="BIND_QUEUE_TO_EXCHANGE_FAILED", message=str(error))
            )

    def setup(self, callback: Optional[Callable[[Any], Result]]):
        try:
            self.channel().unwrap().queue_declare(
                queue=self.name(),
                durable=self.is_durable(),
                exclusive=self._is_exclusive,
                auto_delete=self._is_auto_deleted,
                callback=lambda _: unsafe_panic(callback)(self)
                if callback is not None
                else None,
            )
        except Exception as error:
            raise MainException(code="QUEUE_OPEN_FAILED", message=str(error))

    def is_queue_ready(self):
        return self._is_queue_ready

    def set_queue_ready_status(self, is_ready: bool):
        self._is_queue_ready = is_ready
