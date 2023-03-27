from abc import abstractmethod
from typing import Any, Optional, Union

from returns.future import FutureResult
from returns.maybe import Maybe


class AbstractKeyValueRepository:
    _prefix: str

    def __init__(self, prefix: str) -> None:
        self._prefix = prefix

    def prefix(self):
        return self._prefix

    @abstractmethod
    def set(
        self,
        key: str,
        value: Union[bytes, memoryview, str, int, float],
        expired_seconds: Optional[int] = None,
    ) -> FutureResult:
        pass

    @abstractmethod
    def get(self, key: str) -> FutureResult[Maybe, Any]:
        pass
