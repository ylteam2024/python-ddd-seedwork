import typing as t

T = t.TypeVar("T", bound=t.Callable)


def is_callable_type(tp) -> bool:
    origin = getattr(tp, "__origin__", None)
    return origin is t.Callable.__origin__  # type: ignore


class ReturnType(t.Generic[T]):
    def __class_getitem__(cls, tp):
        if is_callable_type(tp):
            if tp is t.Callable:
                raise TypeError("ReturnType should be parameterized")
            else:
                return_type = tp.__args__[-1]
                return return_type
        else:
            raise TypeError("ReturnType's parameter should be Callable")
