def get_local_classname(instance):
    return get_class_name(instance)


def get_class_name(instance):
    return instance.__class__.__name__
