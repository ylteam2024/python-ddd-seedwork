from abc import abstractmethod
from typing import Generic, TypeVar

from returns.result import Result

from dino_seedwork_be.domain.exceptions import DomainException

RepositoryModel = TypeVar("RepositoryModel")
AggregateRootModel = TypeVar("AggregateRootModel")


class Mapper(Generic[AggregateRootModel, RepositoryModel]):
    @abstractmethod
    @classmethod
    def to_aggregate(
        cls, a_db_model: RepositoryModel
    ) -> Result[AggregateRootModel, DomainException]:
        pass

    @abstractmethod
    @classmethod
    def to_db(
        cls, an_aggregate: AggregateRootModel
    ) -> Result[RepositoryModel, DomainException]:
        pass
