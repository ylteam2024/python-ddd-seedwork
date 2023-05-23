import uuid
from typing import Any, Optional

from returns.future import FutureResult, FutureSuccess
from returns.pipeline import flow, pipe
from returns.pointfree import bind, lash

from dino_seedwork_be.domain.value_object.UUID import UUID
from dino_seedwork_be.utils.functional import return_v

from .IRepository import EntityType, Repository


class RepositoryUUID(Repository[EntityType]):
    def get_next_id(self, simple: Optional[bool] = False) -> FutureResult[UUID, Any]:
        def check_exist_and_gen() -> FutureResult:
            next_id_candidate = UUID(uuid.uuid4())
            return flow(
                next_id_candidate,
                self.get_by_id,
                bind(
                    pipe(
                        bind(return_v(FutureSuccess(next_id_candidate))),
                        lash(lambda _: check_exist_and_gen()),
                    )
                ),
            )

        next_id_candidate = uuid.uuid4()
        match simple:
            case True:
                return FutureSuccess(UUID(next_id_candidate))
            case False:
                return check_exist_and_gen()

        return FutureSuccess(UUID(next_id_candidate))
