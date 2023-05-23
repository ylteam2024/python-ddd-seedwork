from abc import ABC, abstractmethod
from typing import Any, List

from returns.future import FutureResult
from returns.maybe import Maybe

from .ProcessId import ProcessId
from .TimeConstrainedProcessTracker import TimeConstrainedProcessTracker
from .timeout_event_factory import timeout_factory_type


class TimeConstrainedProcessTrackerRepository(ABC):
    @abstractmethod
    def add(
        self, a_time_constrained_process_tracker: TimeConstrainedProcessTracker
    ) -> FutureResult:
        ...

    @abstractmethod
    def all_timed_out() -> FutureResult[List[TimeConstrainedProcessTracker], Any]:
        ...

    @abstractmethod
    def save(
        self, a_time_constrained_process_tracker: TimeConstrainedProcessTracker
    ) -> FutureResult:
        ...

    @abstractmethod
    def tracker_of_process_id(
        self, a_process_id: ProcessId
    ) -> FutureResult[Maybe[TimeConstrainedProcessTracker], Any]:
        ...

    @abstractmethod
    def timeout_event_factory(self) -> timeout_factory_type:
        ...

    @abstractmethod
    def complete_tracker(self, process_id: ProcessId) -> FutureResult:
        pass
