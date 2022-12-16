from returns.result import Failure

from src.seedwork.logic.assertion_concern import AssertionConcern

aAssertionConcern = AssertionConcern()


class TestAssertionConcern:
    def test_ExceptionComposition(self):
        checkingNum = 0

        def increase(cN: int):
            return cN + 1

        result = (
            aAssertionConcern.assertArgumentEquals(1, 1, "correct")
            .map(lambda _: increase(checkingNum))
            .bind(
                lambda value: aAssertionConcern.assertArgumentFalse(False).map(
                    lambda _: value
                )
            )
            .map(lambda cN: increase(cN))
            .bind(
                lambda value: aAssertionConcern.assertArgumentNotNull("Oke").map(
                    lambda _: value
                )
            )
            .map(lambda cN: increase(cN))
        )

        assert result.unwrap() == 3
