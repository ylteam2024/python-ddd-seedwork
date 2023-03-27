import json
from typing import Generic, TypeVar

import jsonpickle
from returns.result import Failure, Result, Success

from dino_seedwork_be.serializer.AbstractSerializer import AbstractSerializer

from .Notification import Notification

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
                "%s" % str(jsonpickle.encode(aNotification, unpicklable=False))
            )
        except Exception as error:
            return Failure(error)

    def deserialize(self, aJson) -> Result[Notification, Exception]:
        try:
            return Success(Notification.restore(json.loads(aJson)))
        except Exception as error:
            return Failure(error)


NotificationSerializer.ins = NotificationSerializer()
