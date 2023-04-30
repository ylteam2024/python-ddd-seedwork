from dino_seedwork_be.utils.functional import apply


class TestFunctionUtility:
    def test_feed_kwargs(self):
        pass

    def test_apply(self):
        def fn(param_1: str, param_2: int):
            return param_1 + str(param_2)

        assert apply(fn, param_1="fefe", param_2=2) == fn(param_1="fefe", param_2=2)
