from abc import abstractmethod
from typing import List

from returns.curry import partial
from returns.future import FutureResult, FutureSuccess
from returns.iterables import Fold
from returns.pipeline import flow, pipe
from returns.pointfree import bind

from dino_seedwork_be.application import ApplicationLifeCycleUsecase
from dino_seedwork_be.process import TimeConstrainedProcessTrackerRepository
from dino_seedwork_be.storage import DBSessionUser

__all__ = ["AbstractProcessApplicationService"]


class AbstractProcessApplicationService(ApplicationLifeCycleUsecase):

    _process_tracker_repository: TimeConstrainedProcessTrackerRepository

    def process_tracker_repository(self) -> TimeConstrainedProcessTrackerRepository:
        return self._process_tracker_repository

    def __init__(
        self, a_processor_tracker_repository: TimeConstrainedProcessTrackerRepository
    ) -> None:
        self._process_tracker_repository = a_processor_tracker_repository
        super().__init__()

    def get_session_users(self) -> List[DBSessionUser]:
        return [self.process_tracker_repository()]

    @abstractmethod
    def check_for_timedout_processes(self):
        pass

    def _execute_check_for_timedout_process(self) -> FutureResult:
        return flow(
            self.process_tracker_repository().all_timed_out(),
            bind(
                pipe(
                    partial(
                        map,
                        lambda tracker: flow(
                            tracker.inform_process_timedout(
                                self.process_tracker_repository().timeout_event_factory()
                            ),
                            bind(
                                lambda _: self.process_tracker_repository().save(
                                    tracker
                                )
                            ),
                        ),
                    ),
                    lambda results: Fold.collect_all(results, FutureSuccess(())),
                )
            ),
        )
