from abc import ABC, abstractmethod
from types import FunctionType

# __all__ = ["Validator"]

# Will be used as an abstract class for Whole Entity Validating Class
# it will be instantiated inside validate method of entity


class Validator(ABC):

    notification_handler: FunctionType

    def __init__(self, notificationHandler: FunctionType):
        self.set_nofitication_handler(notificationHandler)

    def set_nofitication_handler(self, handler: FunctionType):
        self.notification_handler = handler

    @abstractmethod
    def validate(self):
        pass
