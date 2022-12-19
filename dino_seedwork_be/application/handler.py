from abc import abstractmethod
from typing import Any, Generic, TypeVar

from returns.future import FutureResult

from dino_seedwork_be.application.service import AbstractUOWApplicationService

InputType = TypeVar("InputType")
ReturnType = TypeVar("ReturnType")


class BaseHandler(Generic[InputType, ReturnType], AbstractUOWApplicationService):
    @abstractmethod
    def handle(self, command: InputType) -> FutureResult[ReturnType, Any]:
        pass

    def execute(self, command: InputType) -> FutureResult[ReturnType, Any]:
        return self.handle(command)
