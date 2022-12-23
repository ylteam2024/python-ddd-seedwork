from typing import Any, Dict, Type

from returns.maybe import Maybe, Nothing, Some

from dino_seedwork_be.domain.DomainEvent import DomainEvent

__all__ = ["AbstractDomainEventDict"]


class AbstractDomainEventDict:
    _dict: Dict[str, Any] = {}

    # panic
    @classmethod
    def register(cls, name: str, type: Type[DomainEvent]):
        # cls.get_type_by_key(name).map(
        #     lambda _: throwException(
        #         DomainException(
        #             code="TYPE_EXISTED_IN_DOMAIN_MODEL_DICT",
        #             message=f"Type {name} already existed {type}",
        #         )
        #     )
        # )
        cls._dict[name] = type

    @classmethod
    def get_key_by_type(cls, type: Type) -> Maybe[str]:
        for key, value in cls._dict.items():
            match value == type:
                case True:
                    return Some(key)
        return Nothing

    @classmethod
    def get_type_by_key(cls, key: str) -> Maybe[Type[DomainEvent]]:
        print("dict type", cls._dict)
        try:
            return Some(cls._dict[key])
        except KeyError:
            return Nothing
