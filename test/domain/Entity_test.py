from uuid import uuid4

from returns.maybe import Nothing
from returns.result import Result, Success

from dino_seedwork_be.domain.Entity import BaseRawAttributes, Entity
from dino_seedwork_be.domain.value_object.UUID import UUID


class ExampleEntityAttributes(BaseRawAttributes):
    attribute_a: int
    attribute_b: str


class ExampleEntityUUID(Entity[ExampleEntityAttributes, UUID]):
    _attribute_a: int
    _attribute_b: str

    def attribute_a(self) -> int:
        return self._attribute_a

    def attribute_b(self) -> str:
        return self._attribute_b

    def from_atributes(self, raw_attributes: ExampleEntityAttributes) -> Result:
        self._attribute_a = raw_attributes["attribute_a"]
        self._attribute_b = raw_attributes["attribute_b"]
        return Success(None)


class TestEntity:
    def test_created_at_auto(self):
        new_id = UUID(uuid4())
        example_entity = ExampleEntityUUID.create(
            {
                "attribute_a": 1,
                "attribute_b": "tuanpham",
                "created_at": None,
                "updated_at": None,
            },
            new_id,
        ).unwrap()

        assert example_entity.created_at() is not Nothing
        assert example_entity.attribute_a() == 1
        assert example_entity.attribute_b() == "tuanpham"
        assert example_entity.identity() == new_id
