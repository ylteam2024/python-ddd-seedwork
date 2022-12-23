"""
I am message producer, which facilitates sending messages to a BrokerChannel
A BrokerChannel may be either an Exchange or a Queue
"""


from typing import Union

from multimethod import multimethod
from pika import BasicProperties, DeliveryMode
from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, Result, Success, safe

from dino_seedwork_be.adapters.logger import SIMPLE_LOGGER
from dino_seedwork_be.logic.assertion_concern import AssertionConcern

from .BrokerComponent import BrokerComponent
from .exceptions import MessageException
from .Exchange import Exchange
from .MessageParameters import MessageParameters
from .Queue import Queue

__all__ = ["MessageProducer"]


class MessageProducer(AssertionConcern):
    _broker_component: BrokerComponent

    def __init__(self, a_broker_component: BrokerComponent) -> None:
        super().__init__()
        self._broker_component = a_broker_component

    @staticmethod
    def factory(a_broker_component: BrokerComponent) -> "MessageProducer":
        return MessageProducer(a_broker_component)

    def is_ready_for_publish(self) -> bool:
        broker_component = self.broker_component()
        match broker_component:
            case Queue():
                return broker_component.is_queue_ready()
            case Exchange():
                return broker_component.is_exchange_ready()
            case _:
                return False

    def broker_component(self) -> BrokerComponent:
        return self._broker_component

    @multimethod
    def send(self, a_message: Union[str, bytes]) -> Result:
        """
        Answers the receiver after sending a_message to my channel.
        This is a producer ignorance way to use either an exchange or
        a queue channel without requiring it to pass specific parameters.
        By answering myself I allow for sending message bursts.
        @param a_message the String text message to send
        @return MessageProducer
        """
        try:
            self.broker_component().channel().unwrap().basic_publish(
                self.broker_component().exchange_name().value_or(""),
                self.broker_component().queue_name().value_or(""),
                properties=self.text_durability().value_or(None),
                body=a_message,
            )
            return Success(None)
        except Exception as e:
            SIMPLE_LOGGER.error("Error at basic publish a event: %s", e)
            return Failure(
                MessageException(
                    code="SEND_MESSAGE_FAILED",
                    message="Failed to message to channel " + str(e),
                )
            )

    @send.register
    def _(
        self,
        a_message_parameters: MessageParameters,
        a_message: Union[str, bytes],
    ):
        """
        Answers the receiver after sending a_message to my channel
        with a_message_parameters as the message basic properties.
        This is a producer ignorance way to use either an exchange or
        a queue channel without requiring it to pass specific parameters.
        By answering myself I allow for sending message bursts.
        @param a_message_parameters the MessageParameters
        @param a_message the String text message to send
        @return MessageProducer
        """
        print(
            "send message",
            self.broker_component().exchange_name().value_or(""),
            self.broker_component().queue_name().value_or(""),
            self.text_durability().value_or(None),
            a_message,
        )
        return self._check(a_message_parameters).bind(
            safe(
                lambda _: self.broker_component()
                .channel()
                .unwrap()
                .basic_publish(
                    self.broker_component().exchange_name().value_or(""),
                    self.broker_component().queue_name().value_or(""),
                    properties=a_message_parameters.properties(),
                    body=a_message,
                )
            )
        )

    @send.register
    def _(
        self,
        a_routing_key: str,
        a_message_parameters: MessageParameters,
        a_message: Union[str, bytes],
    ) -> Result:
        """
        Answers the receiver after sending a_message to my channel
        with a_routing_key, a_message_parameters as the message basic properties.
        This is a producer ignorance way to use either an exchange or
        a queue channel without requiring it to pass specific parameters.
        By answering myself I allow for sending message bursts.
        @param a_routing_key the String routing key
        @param a_message_parameters the MessageParameters
        @param a_message the String text message to send
        @return MessageProducer
        """

        return self._check(a_message_parameters).bind(
            safe(
                lambda _: self.broker_component()
                .channel()
                .unwrap()
                .basic_publish(
                    self.broker_component().exchange_name().value_or(""),
                    a_routing_key,
                    properties=a_message_parameters.properties(),
                    body=a_message,
                )
            )
        )

    @send.register
    def _(
        self,
        an_exchange: str,
        a_routing_key: str,
        a_message_parameters: MessageParameters,
        a_message: Union[str, bytes],
    ) -> Result:
        """
        Answers the receiver after sending a_message to my channel
        with a_routing_key, a_message_parameters as the message basic properties.
        This is a producer ignorance way to use either an exchange or
        a queue channel without requiring it to pass specific parameters.
        By answering myself I allow for sending message bursts.
        @param an_exchange the String name of the exchange
        @param a_routing_key the String routing key
        @param a_message_parameters the MessageParameters
        @param a_message the String text message to send
        @return MessageProducer
        """

        return self._check(a_message_parameters).bind(
            safe(
                lambda _: self.broker_component()
                .channel()
                .unwrap()
                .basic_publish(
                    an_exchange,
                    a_routing_key,
                    properties=a_message_parameters.properties(),
                    body=a_message,
                )
            )
        )

    def binary_durability(self) -> Maybe[BasicProperties]:
        match self.broker_component().is_durable():
            case True:
                return Some(
                    BasicProperties(
                        content_type="application/octet-stream",
                        delivery_mode=DeliveryMode.Persistent,
                        priority=0,
                    ),
                )
            case False:
                return Nothing

    def text_durability(self) -> Maybe[BasicProperties]:
        match self.broker_component().is_durable():
            case True:
                return Some(
                    BasicProperties(
                        content_type="text/plain",
                        delivery_mode=DeliveryMode.Transient,
                        priority=0,
                    )
                )
            case False:
                return Nothing

    def _check(self, a_message_parameters) -> Result:
        return self.assert_state_false(
            self.broker_component().is_durable() != a_message_parameters.is_durable(),
            code="MSG_PARAMETER_DURABLE_NOT_MATCH_WITH_BROKER",
            aMessage="message parameter durable property is not match with broker component durable",
        )

    def run(self):
        self.broker_component().run()

    def close(self):
        """
        Closes me, which closes my broker channel.
        """
        self.broker_component().close()
