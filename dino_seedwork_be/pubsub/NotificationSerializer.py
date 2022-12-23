import json
from typing import Any, Generic, Type, TypeVar

from returns.result import Failure, Result, Success

from dino_seedwork_be.pubsub.Notification import Notification
from dino_seedwork_be.serializer.AbstractSerializer import AbstractSerializer

NotificationT = TypeVar("NotificationT", bound=Notification)

__all__ = ["NotificationSerializer"]


class NotificationSerializer(
    AbstractSerializer,
    Generic[NotificationT],
):
    ins: "NotificationSerializer"

    @staticmethod
    def instance() -> "NotificationSerializer":
        return NotificationSerializer.ins

    def serialize(self, aNotification: NotificationT) -> Result[str, Exception]:
        try:
            return Success(
                "%s"
                % str(self.json_marshaller().encode(aNotification, unpicklable=False))
            )
        except Exception as error:
            return Failure(error)

    def deserialize(self, aJson) -> Result[Notification, Exception]:
        try:
            return Success(Notification.restore(json.loads(aJson)))
        except Exception as error:
            return Failure(error)


NotificationSerializer.ins = NotificationSerializer()
