import json
import xml.etree.ElementTree as elementTree

import httpx
import validators

validator_utils = validators

__all__ = [
    "validator_utils",
    "Validator",
    "is_in_json_format",
    "is_xml",
    "is_url_image",
]


class Validator:
    @staticmethod
    def email(a_value: str):
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
