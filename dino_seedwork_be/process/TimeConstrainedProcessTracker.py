from datetime import datetime, timedelta
from typing import Any, Type

from multimethod import multimethod
from returns.functions import tap
from returns.future import FutureResult, FutureSuccess
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.result import Result, Success

from dino_seedwork_be.domain import DomainEvent, DomainEventPublisher
from dino_seedwork_be.logic import AssertionConcern
from dino_seedwork_be.process import ProcessId
from dino_seedwork_be.utils import (apply, feed_kwargs, now_utc, return_v,
                                    set_protected_attr)

from .timeout_event_factory import timeout_factory_type


class TimeConstrainedProcessTracker(AssertionConcern):
    _allowable_duration: int
    _completed: bool = False
    _concurrency_version: int = 0
    _description: str
    _process_id: ProcessId
    _process_informed_of_timeout: bool
    _process_timeout_event_type: str
    _retry_count: int = 0
    _timeout_occurs_on: datetime
    _total_retries_permitted: int

    @multimethod
    def __init__(self) -> None:
        super().__init__()

    def __eq__(self, other):
        if isinstance(other, TimeConstrainedProcessTracker):
            return other.process_id().id() == self.process_id().id()
        return False

    @multimethod
    @__init__.register
    def _(
        self,
        a_process_id: ProcessId,
        timeout_occurs_on: datetime,
        an_allowable_duration: int,
        a_retry_count: int,
        a_total_retries_permitted: int,
        a_process_timedout_event_type: str,
        is_process_informed_of_timeout: bool,
        completed: bool,
        a_description: str = "",
    ):
        flow(
            a_process_id,
            self.set_process_id,
            bind(apply(self.set_description, a_description)),
            bind(apply(self.set_timeout_occurs_on, timeout_occurs_on)),
            bind(apply(self.set_allowable_duration, an_allowable_duration)),
            bind(apply(self.set_total_retries_permitted, a_total_retries_permitted)),
            bind(apply(self.set_retry_count, a_retry_count)),
            bind(
                apply(
                    self.set_process_timeout_event_type, a_process_timedout_event_type
                )
            ),
            bind(
                apply(
                    self.set_process_informed_of_timeout, is_process_informed_of_timeout
                )
            ),
            bind(apply(self.set_completed, completed)),
        ).unwrap()

    @staticmethod
    def factory(
        a_process_id: ProcessId,
        an_original_start_time: datetime,
        an_allowable_duration: int,
        a_total_retries_permitted: int,
        a_process_timedout_event_type: str,
        a_description: str = "",
    ) -> Result["TimeConstrainedProcessTracker", Any]:
        a_new_tracker = TimeConstrainedProcessTracker()
        return flow(
            None,
            lambda _: a_new_tracker.set_process_id(a_process_id),
            bind(lambda _: a_new_tracker.set_description(a_description)),
            bind(
                lambda _: a_new_tracker.set_timeout_occurs_on(
                    an_original_start_time + timedelta(seconds=an_allowable_duration)
                )
            ),
            bind(
                lambda _: a_new_tracker.set_total_retries_permitted(
                    a_total_retries_permitted
                )
            ),
            bind(
                lambda _: a_new_tracker.set_process_timeout_event_type(
                    a_process_timedout_event_type
                )
            ),
            bind(lambda _: a_new_tracker.set_allowable_duration(an_allowable_duration)),
            map_(return_v(a_new_tracker)),
        )

    def allowable_duration(self) -> int:
        return self._allowable_duration

    def completed(self) -> bool:
        return self._completed

    def set_completed(self, a_bool: bool) -> Result:
        self._completed = a_bool
        return Success(None)

    def description(self) -> str:
        return self._description

    def set_description(self, a_str: str) -> Result:
        self._description = a_str
        return Success(None)

    def process_id(self) -> ProcessId:
        return self._process_id

    def set_process_id(self, a_process_id) -> Result:
        self._process_id = a_process_id
        return Success(None)

    def is_process_informed_of_timeout(self) -> bool:
        return self._process_informed_of_timeout

    def process_timeout_event_type(self) -> str:
        return self._process_timeout_event_type

    def set_process_timeout_event_type(self, a_type: str) -> Result:
        self._process_timeout_event_type = a_type
        return Success(None)

    def timeout_occurs_on(self) -> datetime:
        return self._timeout_occurs_on

    def has_timed_out(self) -> bool:
        return now_utc() >= self.timeout_occurs_on()

    def total_retries_permitted(self) -> int:
        return self._total_retries_permitted

    def set_total_retries_permitted(self, a_num: int) -> Result:
        self._total_retries_permitted = a_num
        return Success(None)

    def total_retries_reached(self):
        return self.retry_count() > self.total_retries_permitted()

    def retry_count(self) -> int:
        return self._retry_count

    def set_retry_count(self, a_num: int) -> Result:
        return flow(
            {
                "a_value": a_num,
                "a_minium": 0,
                "a_maximum": self.total_retries_permitted() + 1,
                "code": "RETRY_COUNT_VALID_VALUE",
            },
            feed_kwargs(self.assert_argument_range),
            map_(tap(lambda _: set_protected_attr(self, "_retry_count", a_num))),
        )

    def process_timeout_event(
        self, timeout_event_factory: timeout_factory_type
    ) -> DomainEvent:
        return timeout_event_factory(
            self.process_timeout_event_type(),
            self.process_id(),
            self.retry_count(),
            self.total_retries_permitted(),
            now_utc(),
        )

    def set_process_informed_of_timeout(self, a_bool: bool) -> Result:
        self._process_informed_of_timeout = a_bool
        return Success(None)

    def set_timeout_occurs_on(self, a_datetime: datetime) -> Result:
        self._timeout_occurs_on = a_datetime
        return Success(None)

    def set_allowable_duration(self, an_allowable_duration: int) -> Result:
        return self.assert_argument_larger_than(
            an_allowable_duration, 0, code="ALLOW_DURATION_MUST_BE_LARGER_THAN_ZERO"
        ).map(
            tap(
                lambda _: set_protected_attr(
                    self, "_allowable_duration", an_allowable_duration
                )
            )
        )

    def increment_retry_count(self):
        self._retry_count += 1

    def is_completed(self) -> bool:
        return self._completed

    def inform_process_timedout(
        self, timeout_event_factory: timeout_factory_type
    ) -> FutureResult:
        match not self.is_process_informed_of_timeout() and self.has_timed_out():
            case True:
                match self.total_retries_permitted():
                    case 0:
                        return flow(
                            self.process_timeout_event(timeout_event_factory),
                            map_(DomainEventPublisher.instance().publish),
                            map_(
                                tap(
                                    lambda _: self.set_process_informed_of_timeout(True)
                                )
                            ),
                        )
                    case _:

                        def update_tracker():
                            self.increment_retry_count()
                            match self.total_retries_reached():
                                case True:
                                    self.set_process_informed_of_timeout(True)
                                case False:
                                    self.set_timeout_occurs_on(
                                        now_utc()
                                        + timedelta(seconds=self.allowable_duration())
                                    )

                        update_tracker()

                        return flow(
                            self.process_timeout_event(timeout_event_factory),
                            DomainEventPublisher.instance().publish,
                        )
        return FutureSuccess(None)
