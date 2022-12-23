from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from dino_seedwork_be.process.ProcessId import ProcessId

__all__ = ["ProcessCompletionType", "IProcess"]


class ProcessCompletionType(Enum):
    NOT_COMPLETED = "NOT_COMPLETED"
    COMPLETED_NORMALLY = "COMPLETED_NORMALLY"
    TIMED_OUT = "TIMED_OUT"


class IProcess(ABC):
    @abstractmethod
    def allowable_duration() -> int:
        ...

    @abstractmethod
    def can_timeout() -> bool:
        ...

    @abstractmethod
    def current_duration() -> int:
        ...

    @abstractmethod
    def description() -> str:
        ...

    @abstractmethod
    def did_processing_complete() -> bool:
        ...

    @abstractmethod
    def inform_timeout_date(self, a_time_out_date: datetime):
        ...

    @abstractmethod
    def is_completed() -> bool:
        ...

    @abstractmethod
    def is_timeout() -> bool:
        ...

    def is_not_completed(self) -> bool:
        return not self.is_completed()

    @abstractmethod
    def process_completion_type(self) -> ProcessCompletionType:
        ...

    def process_id(self) -> ProcessId:
        ...

    def start_time(self) -> datetime:
        ...

    def time_constrained_process_tracker(self):
        ...
