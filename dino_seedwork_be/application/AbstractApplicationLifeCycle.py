from abc import ABC, abstractmethod
from traceback import print_exception
from typing import Callable, Dict, Generic, List, Optional
from uuid import uuid4

from returns.functions import tap
from returns.future import FutureResult
from returns.pipeline import flow, managed
from returns.pointfree import alt, bind, lash
from returns.result import safe
from toolz.dicttoolz import dissoc

from dino_seedwork_be.adapters.persistance.sql.DBSessionUser import (
    DBSessionUser, SessionType)
from dino_seedwork_be.domain.event.EventStore import EventStore
from dino_seedwork_be.utils.functional import (apply, tap_excute_future,
                                               tap_failure_execute_future)

from .ApplicationLifeCycleUseCase import ApplicationLifeCycleUsecase

# __all__ = ["AbstractApplicationServiceLifeCycle"]


class AbstractApplicationServiceLifeCycle(ABC, Generic[SessionType]):
    _sessions: Dict = {}
    _event_store: EventStore

    @classmethod
    def event_store(cls) -> EventStore:
        return cls._event_store

    @classmethod
    def sessions(cls):
        return cls._sessions

    @classmethod
    @abstractmethod
    def session_factory(cls):
        pass

    @classmethod
    def add_session(cls, correlation_id: Optional[str] = None):
        correlation_id = correlation_id or str(uuid4())
        cls._sessions[correlation_id] = cls.session_factory()
        return [correlation_id, cls._sessions[correlation_id]]

    @classmethod
    def get_session_by_correlation(cls, correlation_id: str):
        session = cls._sessions[correlation_id]
        match session:
            case None:
                return cls.add_session(correlation_id)[1]
            case _:
                return session

    @classmethod
    @safe
    def remove_session_by_correlation(cls, correlation_id):
        cls._sessions = dissoc(cls._sessions, correlation_id)

    @classmethod
    @abstractmethod
    def initialize(cls):
        ...

    @classmethod
    def get_new_correlation_id(cls) -> str:
        return str(uuid4())

    @classmethod
    def begin(
        cls,
        correlation_id: str,
        db_session_users: List[DBSessionUser[SessionType]],
        usecase: ApplicationLifeCycleUsecase[SessionType],
    ) -> FutureResult:
        return cls.start_db(correlation_id, db_session_users, usecase).bind(
            lambda _: cls.event_listen(correlation_id)
        )

    @classmethod
    def exit(cls, correlation_id, result: FutureResult) -> FutureResult:
        commit_or_rollback_result = flow(
            result,
            bind(tap_excute_future(apply(cls.commit_db, correlation_id))),
            alt(tap(print_exception)),
            lash(tap_failure_execute_future(apply(cls.rollback_db, correlation_id))),
        )
        release_session = lambda *_: FutureResult.from_result(
            cls.remove_session_by_correlation(correlation_id)
        )
        return flow(
            commit_or_rollback_result,
            managed(lambda _: commit_or_rollback_result, release_session),
        )

    @classmethod
    @abstractmethod
    def rollback_db(cls, correlation_id: str) -> FutureResult:
        ...

    @classmethod
    @abstractmethod
    def commit_db(cls, correlation_id: str) -> FutureResult:
        ...

    @classmethod
    @abstractmethod
    def start_db(
        cls,
        correlation_id: str,
        db_session_users: List[DBSessionUser[SessionType]],
        usecase: ApplicationLifeCycleUsecase[SessionType],
    ) -> FutureResult:
        ...

    @classmethod
    @abstractmethod
    def event_listen(cls, correlation_id: str) -> FutureResult:
        ...

    @classmethod
    def life_cycle(cls):
        def decor(target_function: Callable[..., FutureResult]):
            def proxy(*args, **kwargs):
                db_session_users: List[DBSessionUser[SessionType]] = args[
                    0
                ].get_session_users()
                correlation_id = cls.get_new_correlation_id()
                return flow(
                    cls.begin(correlation_id, db_session_users, args[0]),
                    managed(
                        lambda _: target_function(*args, **kwargs),
                        lambda _, result: cls.exit(correlation_id, result),
                    ),
                )

            return proxy

        return decor
