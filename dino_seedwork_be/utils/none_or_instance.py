def none_or_instance(cls, param, *args):
    if param is None:
        return None
    return cls(param, *args)


def none_or_transform(obj, transfomer):
    if obj is None:
        return None
    return transfomer(obj)
