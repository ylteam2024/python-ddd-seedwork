import json
import xml.etree.ElementTree as elementTree

import httpx
import validators
from returns.future import FutureFailure

from dino_seedwork_be.exceptions import MainException

validator_utils = validators


def is_email(a_value: str):
    return validators.email(a_value)


def is_in_json_format(aText: str):
    try:
        json.loads(aText)
        return True
    except ValueError:
        return False


def is_xml(value):
    try:
        elementTree.fromstring(value)
    except elementTree.ParseError:
        return False
    return True


def is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = httpx.head(image_url)
    if r.headers["content-type"] in image_formats:
        return True
    return False


def kw_page_size_validate(function):
    def wrapper(*args, **kwargs):
        page = kwargs["page"]
        size = kwargs["size"]
        if page < 1:
            raise MainException(code="PAGE_INVALID_VALUE")
        if size <= 0:
            raise MainException(code="SIZE_INVALID_VALUE")
        return function(*args, **kwargs)

    return wrapper


def safe_kw_page_size_validate(function):
    def wrapper(*args, **kwargs):
        try:
            page = kwargs["page"]
            size = kwargs["size"]
            if page < 1:
                return FutureFailure(MainException(code="PAGE_INVALID_VALUE"))
            if size <= 0:
                return FutureFailure(MainException(code="SIZE_INVALID_VALUE"))
            return function(*args, **kwargs)
        except KeyError:
            return function(*args, **kwargs)

    return wrapper
