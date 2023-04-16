import json

from firebase_admin import App, messaging
from returns.future import FutureFailure, FutureResult, FutureSuccess

from dino_seedwork_be.adapters.messaging.client_notification.AbstractUserNotificationPushDrivingAdapter import \
    UserNotificationPushDrivingAdapter

__all__ = ["FirebaseNotificationDrivingAdapter"]


class FirebaseNotificationDrivingAdapter(UserNotificationPushDrivingAdapter):
    _app: App

    def __init__(self, app: App) -> None:
        self._app = app
        super().__init__()

    def push_to_device(
        self, content: dict, type: str, device_token: str
    ) -> FutureResult:
        try:
            message = messaging.Message(
                data={"type": type, "content": json.dumps(content, default=str)},
                token=device_token,
            )

            response = messaging.send(message)

            return FutureSuccess(response)
        except Exception as error:
            return FutureFailure(error)
