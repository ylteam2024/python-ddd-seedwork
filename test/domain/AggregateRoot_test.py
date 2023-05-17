from uuid import uuid4

from returns.maybe import Nothing, Some
from returns.result import Result, Success

from dino_seedwork_be.domain.AggregateRoot import AggregateRoot
from dino_seedwork_be.domain.Entity import BaseRawAttributes
from dino_seedwork_be.domain.value_object.UUID import UUID


class ExampleAggAttributes(BaseRawAttributes):
    attribute_a: int
    attribute_b: str


class ExampleAggUUID(AggregateRoot[ExampleAggAttributes, UUID]):
    _attribute_a: int
    _attribute_b: str

    def attribute_a(self) -> int:
        return self._attribute_a

    def attribute_b(self) -> str:
        return self._attribute_b

    def init_by_atributes(self, raw_attributes: ExampleAggAttributes) -> Result:
        self._attribute_a = raw_attributes["attribute_a"]
        self._attribute_b = raw_attributes["attribute_b"]
        return Success(None)


class TestAggregate:
    def test_created_at_auto(self):
        new_id = UUID(uuid4())
        example_agg = ExampleAggUUID.create(
            {
                "attribute_a": 1,
                "attribute_b": "tuanpham",
                "created_at": None,
                "updated_at": None,
            },
            Some(new_id),
        ).unwrap()

        assert example_agg.created_at() is not Nothing
        assert example_agg.attribute_a() == 1
        assert example_agg.attribute_b() == "tuanpham"
        assert example_agg.identity() == new_id
