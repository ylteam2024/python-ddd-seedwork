import os

from dotenv import load_dotenv


def castBoolFromStr(value):
    if value.lower() in ["true", "yes", "on", "1"]:
        value = True
    elif value.lower() in ["false", "no", "not", "off", "0"]:
        value = False
    else:
        raise ValueError(
            f'Incorrect value: "{value}". '
            f"It should be one of [1, 0, true, false, yes, no]"
        )
    return value


def get_env(name, default=None, is_bool=False):
    load_dotenv()
    value = os.environ.get(name)
    if value is not None:
        if is_bool:
            return castBoolFromStr(value)
        else:
            return value
    return default


def getEnv(name, default=None, is_bool=False):
    return get_env(name, default, is_bool)
