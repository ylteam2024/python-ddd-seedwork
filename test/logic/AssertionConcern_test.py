from returns.maybe import Some

from dino_seedwork_be.logic.assertion_concern import AssertionConcern

a_assertion_concern = AssertionConcern()


class TestAssertionConcern:
    def test_ExceptionComposition(self):
        checking_num = 0

        def increase(a_value: int):
            return a_value + 1

        result = (
            a_assertion_concern.assert_argument_equals(
                an_obj1=1, an_obj2=1, a_message=Some("correct")
            )
            .map(lambda _: increase(checking_num))
            .bind(
                lambda value: a_assertion_concern.assert_argument_false(False).map(
                    lambda _: value
                )
            )
            .map(lambda a_value: increase(a_value))
            .bind(
                lambda value: a_assertion_concern.assert_argument_not_null("Oke").map(
                    lambda _: value
                )
            )
            .map(lambda a_value: increase(a_value))
        )

        assert result.unwrap() == 3
