import json
import xml.etree.ElementTree as elementTree

import httpx
import validators

validatorUtils = validators


class Validator:
    @staticmethod
    def email(aValue: str):
        return validators.email(aValue)


def isInJsonFormat(aText: str):
    try:
        json.loads(aText)
        return True
    except ValueError:
        return False


def isXml(value):
    try:
        elementTree.fromstring(value)
    except elementTree.ParseError:
        return False
    return True


def isUrlImage(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = httpx.head(image_url)
    if r.headers["content-type"] in image_formats:
        return True
    return False
