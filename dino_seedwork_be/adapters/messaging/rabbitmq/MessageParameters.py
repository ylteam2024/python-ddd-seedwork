from pika import BasicProperties, DeliveryMode


class MessageParameters:
    _properties: BasicProperties

    def __init__(self, a_properties: BasicProperties) -> None:
        super().__init__()
        self.set_properties(a_properties)

    def properties(self) -> BasicProperties:
        return self._properties

    def set_properties(self, a_properties: BasicProperties):
        self._properties = a_properties

    def is_durable(self) -> bool:
        return self.properties().delivery_mode == 2

    @staticmethod
    def durable_text_parameters(a_type: str, a_message_id: str, a_timestamp: int):
        properties = BasicProperties(
            content_type="text/plain",
            content_encoding=None,
            headers=None,
            delivery_mode=DeliveryMode.Persistent,
            priority=0,
            correlation_id=None,
            reply_to=None,
            expiration=None,
            message_id=a_message_id,
            timestamp=a_timestamp,
            type=a_type,
            user_id=None,
            app_id=None,
            cluster_id=None,
        )
        return MessageParameters(properties)

    @staticmethod
    def text_parameters(a_type: str, a_message_id: str, a_timestamp: int):
        properties = BasicProperties(
            content_type="text/plain",
            content_encoding=None,
            headers=None,
            delivery_mode=DeliveryMode.Transient,
            priority=0,
            correlation_id=None,
            reply_to=None,
            expiration=None,
            message_id=a_message_id,
            timestamp=a_timestamp,
            type=a_type,
            user_id=None,
            app_id=None,
            cluster_id=None,
        )
        return MessageParameters(properties)
