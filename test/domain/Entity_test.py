from uuid import uuid4

from returns.maybe import Nothing, Some
from returns.result import Result, Success

from dino_seedwork_be.domain.Entity import BaseOutsideParams, Entity
from dino_seedwork_be.domain.value_object.UUID import UUID
from dino_seedwork_be.utils.date import now_utc


class ExampleEntityAttributes(BaseOutsideParams):
    attribute_a: int
    attribute_b: str


class ExampleEntityUUID(Entity[ExampleEntityAttributes, UUID]):
    _attribute_a: int
    _attribute_b: str

    def attribute_a(self) -> int:
        return self._attribute_a

    def attribute_b(self) -> str:
        return self._attribute_b

    def from_outside_params(self, outside_params: ExampleEntityAttributes) -> Result:
        self._attribute_a = outside_params["attribute_a"]
        self._attribute_b = outside_params["attribute_b"]
        return Success(None)

    def init_with_params(self) -> Result:
        return Success(None)


class OtherExampleEntityUUID(Entity[ExampleEntityAttributes, UUID]):
    _attribute_a: int
    _attribute_b: str

    def attribute_a(self) -> int:
        return self._attribute_a

    def attribute_b(self) -> str:
        return self._attribute_b

    def from_outside_params(self, raw_attributes: ExampleEntityAttributes) -> Result:
        self._attribute_a = raw_attributes["attribute_a"]
        self._attribute_b = raw_attributes["attribute_b"]
        return Success(None)

    def init_with_params(self) -> Result:
        return Success(None)


def create_new_entity(id: UUID):
    example_entity = ExampleEntityUUID.init(
        {
            "attribute_a": 1,
            "attribute_b": "tuanpham",
            "created_at": Some(now_utc()),
            "updated_at": Nothing,
        },
        Some(id),
    ).unwrap()
    return example_entity


def create_new_other_entity(id: UUID):
    example_entity = OtherExampleEntityUUID.init(
        {
            "attribute_a": 1,
            "attribute_b": "tuanpham",
            "created_at": Some(now_utc()),
            "updated_at": Nothing,
        },
        Some(id),
    ).unwrap()
    return example_entity


class TestEntity:
    def test_created_at_auto(self):
        new_id = UUID(uuid4())
        example_entity = create_new_entity(new_id)

        assert example_entity.created_at() is not Nothing
        assert example_entity.attribute_a() == 1
        assert example_entity.attribute_b() == "tuanpham"
        assert example_entity.identity().unwrap() == new_id

    def test_equality(self):
        mutual_id = UUID(uuid4())
        entity_1 = create_new_entity(mutual_id)
        entity_2 = create_new_entity(mutual_id)
        other_entity = create_new_other_entity(mutual_id)

        assert entity_1 == entity_2
        assert other_entity != entity_1
