"""
I am message producer, which facilitates sending messages to a BrokerChannel
A BrokerChannel may be either an Exchange or a Queue
"""


from typing import Union

from multimethod import multimethod
from pika import BasicProperties, DeliveryMode
from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, Result, Success, safe

from dino_seedwork_be.adapters.logger.SimpleLogger import SIMPLE_LOGGER
from dino_seedwork_be.logic.assertion_concern import AssertionConcern

from .exceptions import MessageException
from .Exchange import Exchange
from .MessageParameters import MessageParameters

# __all__ = ["MessageProducer"]


class MessageProducer(AssertionConcern):
    _exchange: Exchange

    def __init__(self, an_exchange: Exchange) -> None:
        super().__init__()
        self._exchange = an_exchange

    @staticmethod
    def factory(an_exchange: Exchange) -> "MessageProducer":
        return MessageProducer(an_exchange)

    def is_ready_for_publish(self) -> bool:
        return self.exchange().is_exchange_ready()

    def exchange(self) -> Exchange:
        return self._exchange

    @multimethod
    def send(self, a_message: Union[str, bytes], a_routing_key: str = "") -> Result:
        """
        Answers the receiver after sending a_message to my channel.
        This is a producer ignorance way to use either an exchange or
        a queue channel without requiring it to pass specific parameters.
        By answering myself I allow for sending message bursts.
        @param a_message the String text message to send
        @return MessageProducer
        """
        try:
            self.exchange().channel().unwrap().basic_publish(
                self.exchange().exchange_name().value_or(""),
                a_routing_key,
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
        a_routing_key: str = "",
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
        return self._check(a_message_parameters).bind(
            safe(
                lambda _: self.exchange()
                .channel()
                .unwrap()
                .basic_publish(
                    self.exchange().exchange_name().value_or(""),
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
                lambda _: self.exchange()
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
        match self.exchange().is_durable():
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
        match self.exchange().is_durable():
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
            self.exchange().is_durable() != a_message_parameters.is_durable(),
            code=Some("MSG_PARAMETER_DURABLE_NOT_MATCH_WITH_BROKER"),
            a_message=Some(
                "message parameter durable property is not match with broker component durable"
            ),
        )

    def run(self):
        self.exchange().run()

    def close(self):
        """
        Closes me, which closes my broker channel.
        """
        self.exchange().close()
