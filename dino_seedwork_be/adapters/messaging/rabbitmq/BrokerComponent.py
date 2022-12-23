import logging
from abc import ABC, abstractmethod
from typing import Callable, Optional

from multimethod import multimethod
from pika import SelectConnection
from pika.channel import Channel
from pika.connection import ConnectionParameters
from returns.functions import tap
from returns.maybe import Maybe, Nothing, Some
from returns.result import Result

from .ConnectionSettings import ConnectionSettings

# I am an abstract class for all Brocker Component, i include an channel
# that all broker component need to refer to

LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)

LOGGER = logging.getLogger(__name__)

__all__ = ["BrokerComponent"]


class BrokerComponent(ABC):
    # My channel
    _channel: Optional[Channel] = None

    # My connection, which is the connection to my host broker
    _connection: SelectConnection

    # My durable prop, which indicates whether or not messages are durable
    _durable: bool = False

    _connection_settings: ConnectionSettings

    _is_open: bool = False

    _on_setup_finish: Callable

    _name: str

    @multimethod
    def __init__(
        self,
        a_connection_settings: ConnectionSettings,
        a_name: str,
        on_setup_finish: Optional[Callable],
    ) -> None:
        self.set_name(a_name)
        self.set_connection_settings(a_connection_settings)
        connection = self._factory_connection(a_connection_settings)
        self.set_connection(connection)
        self._on_setup_callback = on_setup_finish
        # self.run()

    @__init__.register
    def _(
        self,
        a_broker_channel: "BrokerComponent",
        on_setup_finish: Optional[Callable],
    ):
        """
        Initialize a broker component that reuse connection, channel, and setting
        from an existed component, it is useful for creating a queue that routed by
        an ready exchange
        """
        self.set_connection_settings(a_broker_channel.connection_settings())
        self.set_connection(a_broker_channel.connection())
        a_broker_channel.channel().map(tap(self.set_channel))
        self._on_setup_callback = on_setup_finish
        self.setup(self._on_setup_callback)

    def _factory_connection(
        self,
        a_connection_settings: ConnectionSettings,
    ) -> SelectConnection:
        credentials = a_connection_settings.get_credential()
        con_params = ConnectionParameters(
            host=a_connection_settings.host_name(),
            port=a_connection_settings.port().value_or(
                ConnectionParameters.DEFAULT_PORT
            ),
            virtual_host=a_connection_settings.virtual_host(),
            credentials=credentials.value_or(ConnectionParameters.DEFAULT_CREDENTIALS),
        )

        return SelectConnection(
            con_params,
            on_open_callback=self._on_connection_open,
            on_open_error_callback=self._on_connection_open_error,
            on_close_callback=self._on_connection_closed,
        )

    # TODO: refactor logger info here
    def _on_connection_open(self, _):
        LOGGER.info("Connected success")
        self._open_channel()

    def _on_connection_open_error(self, _, err: Exception):
        LOGGER.error("Connection open failed, reopenning in 5 seconds: %s", err)
        self.connection().ioloop.call_later(5, self.connection().ioloop.stop)

    def _on_connection_closed(self, _, reason):
        self.set_channel(None)
        match self.is_open():
            case True:
                LOGGER.warning(
                    "Connection closed unexpected, reopening in 5s: %s", reason
                )
                self.connection().ioloop.call_later(5, self.connection().ioloop.stop)
            case False:
                LOGGER.info("Deliberately close ioloop on connection closed")
                self.connection().ioloop.stop()

    def _open_channel(self):
        """This method will open a new channel with RabbitMQ by issuing the
        Channel.Open RPC command. When RabbitMQ confirms the channel is open
        by sending the Channel.OpenOK RPC reply, the on_channel_open method
        will be invoked.
        """
        LOGGER.info("Creating a new channel")
        self.connection().channel(on_open_callback=self._on_channel_open)

    def _on_channel_open(self, channel: Channel):
        LOGGER.info("Channel opened")
        self.set_channel(channel)

        LOGGER.info("Adding channel close callback")
        channel.add_on_close_callback(self._on_channel_closed)

        LOGGER.info("Setup detail ...")

        self.setup(self._on_setup_callback)

    def _on_channel_closed(self, channel: Channel, reason: Exception):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.
        :param pika.channel.Channel channel: The closed channel
        :param Exception reason: why the channel was closed
        """
        LOGGER.warning("Channel %i was closed: %s", channel, reason)
        self.set_channel(None)
        match self.is_open():
            case True:
                self.connection().close()

    @abstractmethod
    def setup(self, callback: Optional[Callable[..., Result]]):
        pass

    def host(self) -> str:
        return self.connection_settings().host_name()

    def port(self) -> Maybe[int]:
        return self.connection_settings().port()

    def connection_settings(self) -> ConnectionSettings:
        return self._connection_settings

    def set_connection_settings(self, connection_settings: ConnectionSettings):
        self._connection_settings = connection_settings

    def name(self) -> str:
        return self._name

    def set_name(self, a_name: str):
        self._name = a_name

    def is_durable(self) -> bool:
        return self._durable

    def set_durable(self, a_bool: bool):
        self._durable = a_bool

    def channel(self) -> Maybe[Channel]:
        return Maybe.from_optional(self._channel)

    def connection(self) -> SelectConnection:
        return self._connection

    def set_channel(self, a_channel: Optional[Channel] = None):
        self._channel = a_channel

    def set_connection(self, a_connection: SelectConnection):
        self._connection = a_connection

    # Answer whether or not I am an exchange channel
    def is_exchange(self) -> bool:
        return False

    # Answers my name as the exchange name if I am an Exchange
    # otherwhise the empty string

    def exchange_name(self) -> Maybe[str]:
        return Some(self.name()) if self.is_exchange() else Nothing

    # Answer whether or not I am an queue channel
    def is_queue(self) -> bool:
        return False

    # Answers my name as the queue name if I am an Queue
    # otherwhise the empty string

    def queue_name(self) -> Maybe[str]:
        return Some(self.name()) if self.is_queue() else Nothing

    def is_open(self) -> bool:
        return self._is_open

    def _set_is_open(self, is_open: bool):
        self._is_open = is_open

    def _close_channel(self):
        """Invoke this command to close the channel with RabbitMQ by sending
        the Channel.Close RPC command.
        """

        def exe_with_unnone(_):
            LOGGER.info("Close the channel")
            self.channel().unwrap().close()

        self.channel().bind(tap(exe_with_unnone))

    def _close_connection(self):
        """This method closes the connection to RabbitMQ."""

        self.connection().close()

    def close(self):
        # RabbitMQ doesn't guarantee that if isOpen()
        # answers true that close() will work because
        # another client may be racing to close the
        # same process and/or components. so here just
        # attempt to close, catch and ignore, and move
        # on to next steps is the recommended approach.
        #
        # for the purpose here, the isOpen() checks prevent
        # closing a shared channel and connection that is
        # shared by a subscriber exchange and queue.
        self._set_is_open(False)
        self._close_channel()
        self._close_connection()

    def run(self):
        LOGGER.info("io loop run")
        """Run the example code by connecting and then starting the IOLoop."""
        try:
            self.connection().ioloop.start()
        except Exception:
            # Gracefully close the connection
            self.connection().close()
            # Loop until we're fully closed, will stop on its own
            self.connection().ioloop.start()
