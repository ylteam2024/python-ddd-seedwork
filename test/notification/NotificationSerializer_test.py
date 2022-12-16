from datetime import datetime

from src.seedwork.domain.DomainEvent import DomainEvent
from src.seedwork.pubsub.Notification import Notification
from src.seedwork.pubsub.NotificationSerializer import NotificationSerializer


class TestNotificationSerializer:
    def test_serializer(self):
        test_event = DomainEvent(
            name="TestEvent", occurred_on=datetime.now(), props={"name": "haichan"}
        )
        notification = Notification(1, test_event)

        serializer = NotificationSerializer.instance()

        json = serializer.serialize(notification).unwrap()
        restore_notif = serializer.deserialize(json).unwrap()
        assert restore_notif.type_name() == notification.type_name()
        assert restore_notif.id() == notification.id()
        assert restore_notif.occurred_on() == notification.occurred_on()
        assert restore_notif.version() == notification.version()
        assert restore_notif.event().props()["name"] == "haichan"
