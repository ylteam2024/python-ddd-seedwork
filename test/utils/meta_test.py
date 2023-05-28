class ParentClass:
    def get_last_derived_class_name(self):
        last_derived_class = type(self).__name__
        return last_derived_class


class ChildClass(ParentClass):
    pass


class GrandChildClass(ChildClass):
    pass


class TestMeta:
    def test(self):
        grandchild = GrandChildClass()
        class_name = grandchild.get_last_derived_class_name()
        assert "GrandChildClass" in class_name
