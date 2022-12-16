from typing import List
from returns._internal.pipeline.flow import flow
from toolz.dicttoolz import assoc
from toolz.functoolz import reduce

from src.seedwork.utils.functional import feedKwargs


def keys(v: dict):
    return v.keys()

def values(v: dict):
    return v.values()

def dictToCls(v: dict, keys: List[str], Cls):
    return flow(
            reduce(lambda acc, key: assoc(acc, key, v.get(key, None)), keys, {}),
            feedKwargs(Cls)
        )

def extract(v: dict, keys: List[str]) -> dict:
    return {k: v.get(k, None) for k in keys}
