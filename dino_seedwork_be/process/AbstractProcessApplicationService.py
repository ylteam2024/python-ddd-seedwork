from abc import abstractmethod
from typing import List

from returns.curry import partial
from returns.functions import tap
from returns.future import FutureResult, FutureSuccess
from returns.iterables import Fold
from returns.pipeline import flow, pipe
from returns.pointfree import bind, map_

from src.seedwork.application.ApplicationLifeCycleUseCase import \
    ApplicationLifeCycleUsecase
from src.seedwork.process.TimeConstrainedProcessTrackerRepository import \
    TimeConstrainedProcessTrackerRepository
from src.seedwork.storage.uow import DBSessionUser
from src.seedwork.utils.functional import print_result_with_text


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
