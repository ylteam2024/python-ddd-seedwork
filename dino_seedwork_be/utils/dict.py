from typing import List

from returns._internal.pipeline.flow import flow
from toolz.dicttoolz import assoc
from toolz.functoolz import reduce

from dino_seedwork_be.utils import feed_kwargs

__all__ = ["keys", "values", "dict_to_cls", "extract"]


def keys(v: dict):
    return v.keys()


def values(v: dict):
    return v.values()


def dict_to_cls(v: dict, keys: List[str], Cls):
    return flow(
        reduce(lambda acc, key: assoc(acc, key, v.get(key, None)), keys, {}),
        feed_kwargs(Cls),
    )


def extract(v: dict, keys: List[str]) -> dict:
    return {k: v.get(k, None) for k in keys}
