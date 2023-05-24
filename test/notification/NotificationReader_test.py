from datetime import datetime

from dino_seedwork_be import Notification
from dino_seedwork_be.adapters.messaging.notification.NotificationReader import \
    NotificationReader
from dino_seedwork_be.adapters.messaging.notification.NotificationSerializer import \
    NotificationSerializer
from dino_seedwork_be.domain.DomainEvent import DomainEvent

mock_notification_marshalled = Notification(
    1, DomainEvent(name="HauBiTo", occurred_on=datetime.now(), props={"name": "hauto"})
)

mock_notif_serialized = (
    NotificationSerializer.instance().serialize(mock_notification_marshalled).unwrap()
)
wrong_path_notification_module = "a_wrong_path_notification_class"
wrong_path_event_module = "a_wrong_path_event_module"


class TestNotificationReader:
    def test_reading_correct(self):
        try:
            notification = NotificationReader(mock_notif_serialized)
            assert notification.event_string_value("/props/name").unwrap() == "hauto"
        except Exception as error:
            raise error
