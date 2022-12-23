from typing import Any
from uuid import UUID, uuid4

from returns.result import Failure, Result, Success, safe

from dino_seedwork_be.domain.AbstractIdentity import AbstractIdentity

__all__ = ["ProcessId"]


class ProcessId(AbstractIdentity[str]):
    def __init__(self, id: str) -> None:
        super().__init__(id)

    @staticmethod
    def new_process_id() -> Result["ProcessId", Any]:
        try:
            return Success(ProcessId(str(uuid4())))
        except Exception as error:
            return Failure(error)

    @staticmethod
    def from_existing_id(a_str: str) -> "ProcessId":
        return ProcessId(a_str)

    @safe
    def validate(self, an_id: str):
        UUID(an_id)
        return an_id
