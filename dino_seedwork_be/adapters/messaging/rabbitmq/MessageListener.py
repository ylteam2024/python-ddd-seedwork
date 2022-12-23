from abc import abstractmethod
from datetime import datetime

from multimethod import multimethod
from returns.future import FutureFailure, FutureResult

from dino_seedwork_be.exceptions import MainException

from .MessageType import MessageType

__all__ = ["MessageListener"]


class MessageListener:
    """
    * I am a message listener, which is given each message received
    * by a MessageConsumer. I am also an adapter because I provide
    * defaults for both handleMessage() behaviors. A typical subclass
    * would override one or the other handleMessage() based on its
    * type and leave the remaining handleMessage() defaulted since
    * it will never be used by MessageConsumer.
    *
    """

    # My type, which indicates whether I listen for BINARY or TEXT messages.
    _type: MessageType

    def __init__(self, a_type: MessageType) -> None:
        self.set_type(a_type)

    def type(self) -> MessageType:
        """
        * Answers my type.
        * @return Type
        """
        return self._type

    def set_type(self, a_type: MessageType):
        """
        * Sets my type.
        * @param a_type the Type to set as my type
        """
        self._type = a_type

    @abstractmethod
    @multimethod
    def handle_message(
        self,
        a_type: str,
        a_message_id: str,
        a_time_stamp: datetime,
        a_binary_message: bytes,
        a_delivery_tag: int,
        is_redelivery: bool,
    ) -> FutureResult:

        """
        * Handles a_binary_message. If any MessageException is thrown by
        * my implementor its is_retry() is examined and, if true, the
        * message being handled will be nack'd and re-queued. Otherwise,
        * if its is_retry() is false the message will be rejected/failed
        * (not re-queued). If any other Exception is thrown the message
        * will be considered not handled and is rejected/failed.
        * @param a_type the String type of the message if sent, or null
        * @param a_message_id the String id of the message if sent, or null
        * @param a_timestamp the Date timestamp of the message if sent, or null
        * @param a_binary_message the byte[] containing the binary message
        * @param a_delivery_tag the long tag delivered with the message
        * @param is_redelivery the boolean indicating whether or not this message is a redelivery
        * @throws Exception when any problem occurs and the message must not be acknowledged
        """
        return FutureFailure(
            MainException(
                code="METHOD_NOT_IMPLEMENTED",
                message="Handle message method must be implemented",
            )
        )

    @abstractmethod
    @handle_message.register
    def _(
        self,
        a_type: str,
        a_message_id: str,
        a_time_stamp: datetime,
        a_text_message: str,
        a_delivery_tag: int,
        is_redelivery: bool,
    ):
        """
        * Handles a_text_message. If any MessageException is thrown by
        * my implementor its is_retry() is examined and, if true, the
        * message being handled will be nack'd and re-queued. Otherwise,
        * if its is_retry() is false the message will be rejected/failed
        * (not re-queued). If any other Exception is thrown the message
        * will be considered not handled and is rejected/failed.
        * @param a_type the String type of the message if sent, or null
        * @param a_message_id the String id of the message if sent, or null
        * @param a_timestamp the Date timestamp of the message if sent, or null
        * @param a_text_message the byte[] containing the binary message
        * @param a_delivery_tag the long tag delivered with the message
        * @param is_redelivery the boolean indicating whether or not this message is a redelivery
        * @throws Exception when any problem occurs and the message must not be acknowledged
        """
        return FutureFailure(
            MainException(
                code="METHOD_NOT_IMPLEMENTED",
                message="Handle message method must be implemented",
            )
        )
