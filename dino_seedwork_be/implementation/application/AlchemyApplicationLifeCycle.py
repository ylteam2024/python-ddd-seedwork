from abc import abstractmethod
from typing import Callable, List, Type

from returns.future import FutureResult, FutureSuccess, future_safe
from returns.pipeline import flow
from sqlalchemy.ext.asyncio.session import AsyncSession

from dino_seedwork_be.adapters.logger.SimpleLogger import SIMPLE_LOGGER
from dino_seedwork_be.adapters.persistance.sql.DBSessionUser import (
    DBSessionUser, SuperDBSessionUser)
from dino_seedwork_be.application.AbstractApplicationLifeCycle import \
    AbstractApplicationServiceLifeCycle
from dino_seedwork_be.application.ApplicationLifeCycleUseCase import \
    ApplicationLifeCycleUsecase
from dino_seedwork_be.domain import DomainEventSubscriber
from dino_seedwork_be.domain.DomainEventPublisher import DomainEventPublisher
from dino_seedwork_be.domain.event.EventStoreSubscriber import \
    EventStoreSubscriber
from dino_seedwork_be.implementation.event.sqlalchemy.SqlAlchemyEventStore import (
    SqlAlchemyBaseEvent, SqlAlchemyEventStore)

# __all__ = ["DBSessionDomainEventSubs", "AlchemyApplicationLifeCycle"]


class DBSessionDomainEventSubs(DomainEventSubscriber, SuperDBSessionUser[AsyncSession]):
    pass


class AlchemyApplicationLifeCycle(AbstractApplicationServiceLifeCycle):
    _domain_event_subscribers: List[Callable[[], DBSessionDomainEventSubs]] = []

    @abstractmethod
    @classmethod
    def session_factory(cls):
        pass

    @classmethod
    def initialize(cls, event_store_model: Type[SqlAlchemyBaseEvent]):
        session = cls.session_factory()
        cls._event_store = SqlAlchemyEventStore(event_store_model)
        cls._event_store.set_session(session)
        return super().initialize()

    @classmethod
    def start_db(
        cls,
        correlation_id: str,
        db_session_users: List[DBSessionUser],
        usecase: ApplicationLifeCycleUsecase,
    ) -> FutureResult:
        session = cls.add_session(correlation_id)[1]
        usecase.set_session(session)
        [session_user.set_session(session) for session_user in db_session_users]
        return FutureSuccess(None)

    @classmethod
    def rollback_db(cls, correlation_id: str) -> FutureResult:
        SIMPLE_LOGGER.warning("[rollback_db] deliberately rollback DB")
        return flow(
            correlation_id,
            cls.get_session_by_correlation,
            lambda session: future_safe(session.rollback)(),
        )

    @classmethod
    def commit_db(cls, correlation_id: str) -> FutureResult:
        return flow(
            correlation_id,
            cls.get_session_by_correlation,
            lambda session: future_safe(session.commit)(),
        )

    @classmethod
    def close_db(cls, correlation_id: str) -> FutureResult:
        return flow(
            correlation_id,
            cls.get_session_by_correlation,
            lambda session: future_safe(session.close()),
        )

    @classmethod
    def set_event_subscribers(
        cls, subscribers: List[Callable[[], DBSessionDomainEventSubs]]
    ):
        cls._domain_event_subscribers = subscribers

    @classmethod
    def event_listen(cls, correlation_id: str) -> FutureResult:
        DomainEventPublisher.instance().reset()
        event_store = cls.event_store()

        DomainEventPublisher.instance().subscribe(EventStoreSubscriber(event_store))
        for publisher_factory in cls._domain_event_subscribers:
            publisher = publisher_factory()
            publisher.set_session(cls.get_session_by_correlation(correlation_id))
            DomainEventPublisher.instance().subscribe(publisher)

        return FutureSuccess("OK")
