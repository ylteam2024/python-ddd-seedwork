from abc import ABC, abstractmethod


class AbstractLogger(ABC):

    _tag: str

    def __init__(self, tag: str):
        self.set_tag(tag)

    def set_tag(self, a_tag: str):
        self._tag = a_tag

    def tag(self) -> str:
        return self._tag

    @abstractmethod
    def info(self, message: str):
        pass

    @abstractmethod
    def error(self, message: str):
        pass

    @abstractmethod
    def warning(self, message: str):
        pass
