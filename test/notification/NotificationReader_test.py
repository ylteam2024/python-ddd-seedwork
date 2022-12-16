from src.seedwork.domain.DomainEvent import DomainEvent
from src.seedwork.pubsub.NotificationReader import NotificationReader

mock_notification_marshalled = '{"py/object": "src.seedwork.pubsub.Notification.Notification", "_id": 1, "_event": {"py/object": "src.modules.ai_market.domain.model.package.InitOfferingRequestEvent.InitOfferingRequestEvent", "_version": 0, "_occurred_on": {"py/object": "datetime.datetime", "__reduce__": [{"py/type": "datetime.datetime"}, ["B+YLFgcyDAEVfw==", {"py/reduce": [{"py/type": "datetime.timezone"}, {"py/tuple": [{"py/reduce": [{"py/type": "datetime.timedelta"}, {"py/tuple": [0, 0, 0]}]}]}]}]]}, "_name": "InitOfferingRequestEvent", "_onchain_id": 62, "_number_of_request": 200, "_unit_price": 0.001, "_package_offering_id": {"py/object": "src.seedwork.domain.value_objects.ID", "_ID__id": {"py/reduce": [{"py/type": "asyncpg.pgproto.pgproto.UUID"}, {"py/tuple": [{"py/b64": "WPyPpeaXQ/aMHmkelMHH8g=="}]}]}}}, "_occurred_on": {"py/id": 2}, "_type_name": "InitOfferingRequestEvent", "_version": 0}'
wrong_path_notification_module = "a_wrong_path_notification_class"
wrong_path_event_module = "a_wrong_path_event_module"


class TestNotificationReader:
    def test_reading_correct(self):
        try:
            notification = NotificationReader(mock_notification_marshalled)
            match notification.event():
                case DomainEvent():
                    assert True
                case _:
                    assert False
        except Exception as error:
            raise error

    def test_reading_event_wrong_module_path(self):
        try:
            wrong_event_path_notif_json = mock_notification_marshalled.replace(
                "src.modules.ai_market.domain.model.package.InitOfferingRequestEvent.InitOfferingRequestEvent",
                wrong_path_event_module,
            )
            notification = NotificationReader(wrong_event_path_notif_json)
            match notification.event():
                case DomainEvent():
                    assert True
                case _:
                    assert False
        except Exception as error:
            raise error
