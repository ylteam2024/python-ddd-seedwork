from test.mock.MockEventHandlingTracker import MockEventHandlingTracker
from typing import Callable, List

import pytest
from redis import Redis
from returns.future import FutureResult, FutureSuccess

from dino_seedwork_be.adapters.messaging.implement.rabbitmq.ExchangeListener import \
    ExchangeListener
from dino_seedwork_be.adapters.messaging.notification.EventHandlingTracker import \
    EventHandlingTracker
from dino_seedwork_be.adapters.messaging.notification.KeyValueEventHandlingTracker import \
    KeyValueEventHandlingTracker
from dino_seedwork_be.adapters.persistance.key_value.RedisRepository import \
    RedisPyRepository
from dino_seedwork_be.utils.functional import unwrap_future_result


@pytest.fixture(scope="session")
def mock_notification_tracker():
    yield MockEventHandlingTracker()


@pytest.fixture(scope="session")
def redis_notification_tracker():
    redis = Redis(
        host="localhost",
        port=6379,
        decode_responses=True,
        password="123456",
        # username="dino",
    )
    key_value_repository = RedisPyRepository(redis, "test-ai-market")
    key_value_event_handling_tracker = KeyValueEventHandlingTracker(
        key_value_repository
    )
    yield key_value_event_handling_tracker


class MockListener(ExchangeListener):
    notification_tracker: EventHandlingTracker
    dispatch_callback: Callable

    def __init__(
        self, cb: Callable, notification_tracker: EventHandlingTracker
    ) -> None:
        self.dispatch_callback = cb
        self.notification_tracker = notification_tracker
        super().__init__()

    def exchange_name(self) -> str:
        return "MOCK_EXCHANGE"

    def filtered_dispatch(self, a_type: str, a_text_message: str) -> FutureResult:
        self.dispatch_callback()
        return FutureSuccess(None)

    def listen_to(self) -> List[str]:
        return ["mock_type_message"]

    def queue_name(self) -> str:
        return "MOCK_QUEUE_NAME"


class TestExchangeListener:
    dispatch_callback_called: bool = False

    async def test_idempotent_dispatch_handler(
        self, mock_notification_tracker: MockEventHandlingTracker
    ):
        def cb():
            self.dispatch_callback_called = True

        mock_listener = MockListener(cb, mock_notification_tracker)

        message_id = "mock_message_id"

        await mock_listener.itempotent_handle_dispatch(
            message_id, "mock_type_message", b"mock_content"
        ).awaitable()

        assert mock_notification_tracker._store[message_id] == True

        assert self.dispatch_callback_called is True

        self.dispatch_callback_called = False

    async def test_idempotent_dispatch_handler_passing(
        self, mock_notification_tracker: MockEventHandlingTracker
    ):
        def cb():
            self.dispatch_callback_called = True

        mock_listener = MockListener(cb, mock_notification_tracker)

        message_id = "mock_message_id"
        mock_notification_tracker._store[message_id] = True

        await mock_listener.itempotent_handle_dispatch(
            message_id, "mock_type_message", b"mock_content"
        ).awaitable()

        assert self.dispatch_callback_called is False

        self.dispatch_callback_called = False

    async def test_idempotent_dispatch_handler_with_redis(
        self, redis_notification_tracker: KeyValueEventHandlingTracker
    ):
        dispatch_callback_called = False

        def cb():
            nonlocal dispatch_callback_called
            dispatch_callback_called = True

        mock_listener = MockListener(cb, redis_notification_tracker)

        message_id = "mock_message_id"

        await unwrap_future_result(
            mock_listener.itempotent_handle_dispatch(
                message_id, "mock_type_message", b"mock_content"
            )
        )

        assert dispatch_callback_called is True

        assert (
            await unwrap_future_result(
                redis_notification_tracker.check_if_notif_handled(message_id)
            )
            == True
        )

        await unwrap_future_result(
            redis_notification_tracker.unmark_notif_as_handled(message_id)
        )

    async def test_idempotent_dispatch_handler_passing_with_redis(
        self, redis_notification_tracker: KeyValueEventHandlingTracker
    ):
        dispatch_callback_called = False

        def cb():
            nonlocal dispatch_callback_called
            dispatch_callback_called = True

        mock_listener = MockListener(cb, redis_notification_tracker)

        message_id = "mock_message_id"

        await unwrap_future_result(
            redis_notification_tracker.mark_notif_as_handled(message_id)
        )

        await unwrap_future_result(
            mock_listener.itempotent_handle_dispatch(
                message_id, "mock_type_message", b"mock_content"
            )
        )

        assert dispatch_callback_called is False

        await unwrap_future_result(
            redis_notification_tracker.unmark_notif_as_handled(message_id)
        )
