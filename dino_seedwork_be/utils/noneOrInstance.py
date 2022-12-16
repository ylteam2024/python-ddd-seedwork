def noneOrInstance(cls, param, *args):
    if param is None:
        return None
    return cls(param, *args)


def noneOrTransform(obj, transfomer):
    if obj is None:
        return None
    return transfomer(obj)
