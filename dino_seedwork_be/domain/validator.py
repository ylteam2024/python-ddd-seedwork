from abc import abstractmethod
from types import FunctionType


# Will be used as an abstract class for Whole Entity Validating Class
# it will be instantiated inside validate method of entity
class Validator:
    notificationHandler: FunctionType

    def __init__(self, notificationHandler: FunctionType):
        self.setNofiticationHandler(notificationHandler)

    def setNofiticationHandler(self, handler: FunctionType):
        self.notificationHandler = handler

    @abstractmethod
    def validate(self):
        pass
