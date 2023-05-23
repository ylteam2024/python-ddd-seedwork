from typing import Any, Callable, Optional

from pika.exchange_type import ExchangeType
from returns.maybe import Maybe
from returns.result import Result, safe

from dino_seedwork_be.adapters.logger.SimpleLogger import SIMPLE_LOGGER
from dino_seedwork_be.utils.functional import execute

from .BrokerComponent import BrokerComponent
from .ConnectionSettings import ConnectionSettings

# __all__ = ["Exchange"]


class Exchange(BrokerComponent):
    _type: ExchangeType
    _is_exchange_ready: bool = False
    _is_auto_delete: bool = False

    def is_exchange(self) -> bool:
        return True

    def set_exchange_ready_status(self, a_bool: bool):
        self._is_exchange_ready = a_bool

    def is_exchange_ready(self) -> bool:
        return self._is_exchange_ready

    def __init__(
        self,
        a_con_settings: ConnectionSettings,
        a_name: str,
        a_type: ExchangeType,
        is_durable: bool,
        is_auto_delete: bool = False,
        on_setup_finish: Optional[Callable[..., Result]] = None,
    ) -> None:
        super().__init__(a_name, a_con_settings, None, on_setup_finish)
        self.set_type(a_type)
        self.set_durable(is_durable)
        self._is_auto_delete = is_auto_delete

    @staticmethod
    @safe
    def factory(
        a_con_settings: ConnectionSettings,
        a_name: str,
        a_type: ExchangeType,
        is_durable: bool,
        is_auto_delete: bool = False,
        on_setup_finish: Optional[Callable[..., Result]] = None,
    ):
        return Exchange(
            a_con_settings, a_name, a_type, is_durable, is_auto_delete, on_setup_finish
        )

    @staticmethod
    @safe
    def direct_instance(
        a_con_settings: ConnectionSettings,
        a_name: str,
        is_durable: bool,
        is_auto_delete: bool = False,
        on_setup_finish: Optional[Callable[..., Result]] = None,
    ) -> "Exchange":
        return Exchange(
            a_con_settings,
            a_name,
            ExchangeType.direct,
            is_durable,
            is_auto_delete,
            on_setup_finish=on_setup_finish,
        )

    @staticmethod
    @safe
    def fanout_instance(
        a_con_settings,
        a_name: str,
        is_durable: bool,
        is_auto_delete: bool = False,
        on_setup_finish: Optional[Callable[..., Result]] = None,
    ) -> "Exchange":
        return Exchange(
            a_con_settings,
            a_name,
            ExchangeType.fanout,
            is_auto_delete,
            is_durable,
            on_setup_finish=on_setup_finish,
        )

    @staticmethod
    @safe
    def headers_instance(
        a_con_settings,
        a_name: str,
        is_durable: bool,
        is_auto_delete: bool = False,
        on_setup_finish: Optional[Callable[..., Result]] = None,
    ) -> "Exchange":
        return Exchange(
            a_con_settings,
            a_name,
            ExchangeType.headers,
            is_durable,
            is_auto_delete,
            on_setup_finish=on_setup_finish,
        )

    @staticmethod
    @safe
    def topic_instance(
        a_con_settings,
        a_name: str,
        is_durable: bool,
        is_auto_delete: bool = False,
        on_setup_finish: Optional[Callable[..., Result]] = None,
    ) -> "Exchange":
        return Exchange(
            a_con_settings,
            a_name,
            ExchangeType.topic,
            is_durable,
            is_auto_delete,
            on_setup_finish=on_setup_finish,
        )

    def type(self) -> ExchangeType:
        return self._type

    def set_type(self, a_type: ExchangeType):
        self._type = a_type

    @safe
    def setup(self, callback: Optional[Callable[[Any], Result]] = None):
        SIMPLE_LOGGER.info("setup an exchange %s", self.name())

        def on_exchange_declare_ok(_):
            SIMPLE_LOGGER.info("delare exchange %s successfully :)", self.name())
            self.set_exchange_ready_status(True)
            Maybe.from_optional(execute(callback, self)).map(
                lambda result: result.unwrap()
            )

        self.channel().unwrap().exchange_declare(
            exchange=self.name(),
            exchange_type=self.type(),
            durable=self.is_durable(),
            auto_delete=self._is_auto_delete,
            callback=on_exchange_declare_ok,
        )
