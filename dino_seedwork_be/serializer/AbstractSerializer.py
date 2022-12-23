import jsonpickle

__all__ = ["AbstractSerializer"]


class AbstractSerializer:
    __json = jsonpickle

    def json_marshaller(self):
        return self.__json
