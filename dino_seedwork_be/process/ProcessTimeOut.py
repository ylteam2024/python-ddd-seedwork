from datetime import datetime

from dino_seedwork_be.domain.DomainEvent import DomainEvent
from dino_seedwork_be.process.ProcessId import ProcessId
from dino_seedwork_be.utils.date import now_utc


class ProcessTimedOut(DomainEvent):
    _event_verion: int
    _process_id: ProcessId
    _retry_count: int
    _total_retries_permitted: int

    def __init__(
        self,
        type: str,
        a_process_id: ProcessId,
        retry_count: int = 0,
        a_total_retries_permitted: int = 0,
        occurred_on: datetime = now_utc(),
    ):
        super().__init__(name=type, occurred_on=occurred_on)
        self._process_id = a_process_id
        self._retry_count = retry_count
        self._event_verion = 1
        self._total_retries_permitted = a_total_retries_permitted

    @staticmethod
    def factory(
        type: str,
        a_process_id: ProcessId,
        a_retry_count: int = 0,
        a_total_retries_permitted: int = 0,
        occurred_on: datetime = now_utc(),
    ):
        return ProcessTimedOut(
            type, a_process_id, a_retry_count, a_total_retries_permitted, occurred_on
        )

    def allow_retries(self) -> bool:
        return self.total_retries_permitted() > 0

    def total_retries_permitted(self) -> int:
        return self._total_retries_permitted

    def has_fully_timedout(self):
        return not self.allow_retries() or self.total_retries_reached()

    def total_retries_reached(self):
        return self.retry_count() >= self.total_retries_permitted()

    def retry_count(self) -> int:
        return self._retry_count
