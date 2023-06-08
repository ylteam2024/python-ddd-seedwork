from pytest import fixture
from returns.maybe import Maybe, Nothing, Some
from returns.result import Result, Success

from dino_seedwork_be.domain.Entity import BaseOutsideParams, Entity
from dino_seedwork_be.domain.value_object.NID import NID
from dino_seedwork_be.utils.functional import unwrap_future_result
from dino_seedwork_be.utils.test.MockRepository import MockRepository


class MockEntityAttr(BaseOutsideParams):
    ...


class MockEntity(Entity[BaseOutsideParams, NID]):
    def from_outside_params(self, _: MockEntityAttr) -> Result:
        return Success(None)

    def create_with_params(self) -> Result:
        return Success(None)


class TestedMockRepository(MockRepository[MockEntity]):
    def init_collection(self):
        self._collection = {
            MockEntity.init(
                {"created_at": Nothing, "updated_at": Nothing}, Some(NID(i))
            ).unwrap()
            for i in range(1, 100)
        }


@fixture(scope="class")
def mock_repository():
    yield TestedMockRepository()


class TestMockRepository:
    async def test_init_collections(self, mock_repository: TestedMockRepository):
        len_dataset = await unwrap_future_result(mock_repository.count())
        assert len_dataset == 99

    async def test_get_by_id(self, mock_repository: TestedMockRepository):
        entity = await unwrap_future_result(mock_repository.get_by_id(NID(55)))
        match entity:
            case Some(e):
                assert e.identity() == Some(NID(55))
            case Maybe.empty:
                assert False

    async def test_add(self, mock_repository: TestedMockRepository):
        added_entity = MockEntity.init(
            {"created_at": Nothing, "updated_at": Nothing}, Some(NID(100))
        ).unwrap()
        await unwrap_future_result(mock_repository.add(added_entity))
        entity = await unwrap_future_result(mock_repository.get_by_id(NID(100)))
        assert entity == Some(added_entity)
