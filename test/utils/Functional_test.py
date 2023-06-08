from returns.functions import tap
from returns.maybe import Nothing, Some
from returns.result import Failure, Success

from dino_seedwork_be.domain.exceptions import DomainException
from dino_seedwork_be.exceptions import MainException
from dino_seedwork_be.fp import (collect_result, collect_result_all,
                                 handle_on_maybe)
from dino_seedwork_be.utils.functional import apply, assert_false, assert_true


class TestFunctionUtility:
    def test_feed_kwargs(self):
        pass

    def test_apply(self):
        def fn(param_1: str, param_2: int):
            return param_1 + str(param_2)

        assert apply(fn, param_1="fefe", param_2=2)(None) == fn(
            param_1="fefe", param_2=2
        )

    def test_handle_on_maybe(self):
        def return_success(_):
            return Success(None)

        def return_failure(_):
            return Failure(DomainException(code="ERROR"))

        result = handle_on_maybe(return_success)(Some(None))

        assert result == Success(None)

        result = handle_on_maybe(return_success)(Nothing)

        assert result == Success(None)

        result = handle_on_maybe(return_failure)(Some(None))

        result.map(tap(assert_false)).alt(tap(assert_true))

        result = handle_on_maybe(return_failure)(Nothing)

        assert result == Success(None)

    def test_collect(self):
        collect_success = collect_result(
            [Success(1), Success(2), Success(3)], Success(())
        )

        match collect_success:
            case Success((1, 2, 3)):
                assert True
            case _:
                assert False

        collect_failure = collect_result(
            [Success(1), Failure(MainException(code="ERROR"))], Success(())
        )

        match collect_failure:
            case Failure(_):
                assert True
            case _:
                assert False

        collect_all_success = collect_result_all(
            [Success(1), Failure(MainException(code="ERROR"))], Success(())
        )
        match collect_all_success:
            case Success((1,)):
                assert True
            case _:
                assert False

        collect_all_failure = collect_result_all(
            [
                Failure(MainException(code="ERROR_1")),
                Failure(MainException(code="ERROR_2")),
            ],
            Failure(()),
        )

        match collect_all_failure:
            case Failure():
                assert True
            case _:
                assert False
