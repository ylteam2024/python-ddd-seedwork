from datetime import datetime
from typing import Callable

from dino_seedwork_be.domain.DomainEvent import DomainEvent
from dino_seedwork_be.process.ProcessId import ProcessId
from dino_seedwork_be.utils.date import now_utc

timeout_factory_type = Callable[[str, ProcessId, int, int, datetime], DomainEvent]

__all__ = ["factory_timeout_event"]


def factory_timeout_event(
    type: str,
    a_process_id: ProcessId,
    retry_count: int = 0,
    a_total_retries_permitted: int = 0,
    occurred_on: datetime = now_utc(),
):
    return DomainEvent(
        type,
        occurred_on=occurred_on,
        props={
            "a_process_id": a_process_id.id(),
            "retry_count": retry_count,
            "total_retries_permitted": a_total_retries_permitted,
        },
    )
