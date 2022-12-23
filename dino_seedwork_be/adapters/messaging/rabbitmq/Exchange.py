from typing import Any, Callable, Optional

from pika.exchange_type import ExchangeType
from returns.result import Result, safe

from dino_seedwork_be.adapters.logger import SIMPLE_LOGGER
from dino_seedwork_be.utils.functional import execute

from .BrokerComponent import BrokerComponent
from .ConnectionSettings import ConnectionSettings

__all__ = ["Exchange"]


class Exchange(BrokerComponent):
    _type: ExchangeType
    _is_exchange_ready: bool = False

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
        a_type: str,
        is_durable: bool,
        on_setup_finish: Optional[Callable] = None,
    ) -> None:
        super().__init__(a_con_settings, a_name, on_setup_finish)
        self.set_type(a_type)
        self.set_durable(is_durable)

    @staticmethod
    @safe
    def direct_instance(
        a_con_settings: ConnectionSettings,
        a_name: str,
        is_durable: bool,
        on_setup_finish: Optional[Callable] = None,
    ) -> "Exchange":
        return Exchange(
            a_con_settings,
            a_name,
            "direct",
            is_durable,
            on_setup_finish=on_setup_finish,
        )

    @staticmethod
    @safe
    def fanout_instance(
        a_con_settings,
        a_name: str,
        is_durable: bool,
        on_setup_finish: Optional[Callable] = None,
    ) -> "Exchange":
        return Exchange(
            a_con_settings,
            a_name,
            "fanout",
            is_durable,
            on_setup_finish=on_setup_finish,
        )

    @staticmethod
    @safe
    def headers_instance(
        a_con_settings,
        a_name: str,
        is_durable: bool,
        on_setup_finish: Optional[Callable] = None,
    ) -> "Exchange":
        return Exchange(
            a_con_settings,
            a_name,
            "headers",
            is_durable,
            on_setup_finish=on_setup_finish,
        )

    @staticmethod
    def topic_instance(
        a_con_settings,
        a_name: str,
        is_durable: bool,
        on_setup_finish: Optional[Callable] = None,
    ) -> "Exchange":
        return Exchange(
            a_con_settings, a_name, "topic", is_durable, on_setup_finish=on_setup_finish
        )

    def type(self) -> ExchangeType:
        return self._type

    def set_type(self, a_type: str):
        self._type = ExchangeType(a_type)

    def setup(self, callback: Optional[Callable[[Any], Result]] = None):
        SIMPLE_LOGGER.info("setup an exchange %s", self.name())

        def on_exchange_declare_ok(_):
            SIMPLE_LOGGER.info("delare exchange %s successfully :)", self.name())
            self.set_exchange_ready_status(True)
            execute(callback, self)

        self.channel().unwrap().exchange_declare(
            exchange=self.name(),
            exchange_type=self.type(),
            durable=self.is_durable(),
            callback=on_exchange_declare_ok,
        )
