import json

from returns.result import safe

from .AbstractSerializer import AbstractSerializer


class SimpleJSONSerializer(AbstractSerializer[dict]):
    @safe
    def serialize(self, obj: dict) -> str:
        return json.dumps(obj)

    @safe
    def deserialize(self, an_json: str) -> dict:
        return json.loads(an_json)
