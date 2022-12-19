from returns.result import Failure

from dino_seedwork_be.logic.assertion_concern import AssertionConcern

aAssertionConcern = AssertionConcern()


class TestAssertionConcern:
    def test_ExceptionComposition(self):
        checkingNum = 0

        def increase(cN: int):
            return cN + 1

        result = (
            aAssertionConcern.assert_argument_equals(1, 1, "correct")
            .map(lambda _: increase(checkingNum))
            .bind(
                lambda value: aAssertionConcern.assert_argument_false(False).map(
                    lambda _: value
                )
            )
            .map(lambda cN: increase(cN))
            .bind(
                lambda value: aAssertionConcern.assert_argument_not_null("Oke").map(
                    lambda _: value
                )
            )
            .map(lambda cN: increase(cN))
        )

        assert result.unwrap() == 3
