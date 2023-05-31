from typing import (Callable, Optional, ParamSpec, Tuple, Type, TypeVar, Union,
                    overload)

from returns.result import Result, safe

from dino_seedwork_be.domain.exceptions import DomainException

_FuncParams = ParamSpec("_FuncParams")
_ValueType = TypeVar("_ValueType", covariant=True)


@overload
def domain_safe(
    function: Callable[_FuncParams, _ValueType],
) -> Callable[_FuncParams, Result[_ValueType, DomainException]]:
    """Decorator to convert exception-throwing for any kind of Exception."""


@overload
def domain_safe(
    exceptions: Tuple[Type[Exception], ...],
) -> Callable[
    [Callable[_FuncParams, _ValueType]],
    Callable[_FuncParams, Result[_ValueType, DomainException]],
]:
    """Decorator to convert exception-throwing just for a set of Exceptions."""


def domain_safe(  # type: ignore # noqa: WPS234, C901
    function: Optional[Callable[_FuncParams, _ValueType]] = None,
    exceptions: Optional[Tuple[Type[Exception], ...]] = None,
) -> Union[
    Callable[_FuncParams, Result[_ValueType, DomainException]],
    Callable[
        [Callable[_FuncParams, _ValueType]],
        Callable[_FuncParams, Result[_ValueType, DomainException]],
    ],
]:
    def factory(
        inner_function: Callable[_FuncParams, _ValueType],
        inner_exceptions: Tuple[Type[Exception], ...],
    ):
        def decorator(*args: _FuncParams.args, **kwargs: _FuncParams.kwargs):
            return safe(inner_exceptions)(inner_function)(*args, **kwargs).alt(
                lambda e: DomainException(exception=e)
            )

        return decorator

    if callable(function):
        return factory(function, (Exception,))
    if isinstance(function, tuple):
        exceptions = function  # type: ignore
        function = None
    return lambda function: factory(function, exceptions)  # type: ignore
