import re
import traceback
from datetime import datetime
from decimal import Decimal
from typing import Optional

import jsonpickle
import toolz

from dino_seedwork_be.exceptions import IllegalArgumentException

__all__ = ["JSONReader", "AbstractJSONMediaReader"]


class JSONReader:
    def deserialize(self, aJson: str):
        try:
            object = jsonpickle.decode(aJson)
            return object
        except Exception:
            traceback.print_exc()
            raise RuntimeError


class AbstractJSONMediaReader:
    _representation: dict = {}
    _json_reader: JSONReader

    def __init__(self, a_json: str):
        self.initialize(a_json)

    def json_reader(self):
        return self._json_reader

    def set_representation(self, a_representation: dict):
        self._representation = a_representation

    def get_representation(self):
        return self._representation

    def initialize(self, a_json: str):
        self._json_reader = JSONReader()
        self.set_representation(self.json_reader().deserialize(a_json))

    def get_value(self, path: str, a_dict: Optional[dict] = None):
        if re.match(r"(^(?:\/[a-zA-Z0-9_]+)+$)", path) is None:
            raise IllegalArgumentException(f"Json Path Reader is illegal {path}")
        source = self.get_representation()
        match a_dict is not None:
            case True:
                source = a_dict
        return toolz.dicttoolz.get_in(path.split("/")[1:], source)

    def string_value(self, path: str, a_dict: Optional[dict] = None) -> str | None:
        value = self.get_value(a_dict=a_dict, path=path)
        if value is None:
            return None
        return str(value)

    def big_decimal_value(
        self, path: str, a_dict: Optional[dict] = None
    ) -> Decimal | None:
        strValue = self.string_value(path, a_dict=a_dict)
        if strValue is None:
            return None
        return Decimal(strValue)

    def boolean_value(self, path: str, a_dict: Optional[dict] = None) -> bool | None:
        str_value = self.string_value(path, a_dict=a_dict)
        if str_value is None:
            return None
        match str_value:
            case "True" | "true":
                return True
            case "False" | "false":
                return False
            case _:
                return bool(str_value)

    def datetime_value(
        self, path: str, a_dict: Optional[dict] = None
    ) -> datetime | None:
        str_value = self.string_value(path, a_dict=a_dict)
        if str_value is None:
            return None
        return datetime.fromisoformat(str_value)

    def float_value(self, path: str, a_dict: Optional[dict] = None) -> float | None:
        str_value = self.string_value(path, a_dict=a_dict)
        if str_value is None:
            return None
        return float(str_value)

    def int_value(self, path: str, a_dict: Optional[dict] = None) -> int | None:
        str_value = self.string_value(path, a_dict=a_dict)
        if str_value is None:
            return None
        return int(float(str_value))
