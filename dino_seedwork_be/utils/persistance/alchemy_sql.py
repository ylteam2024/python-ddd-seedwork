from typing import Any, List

from dino_seedwork_be.adapters import Repository

__all__ = [
    "alchemy_execute_query_on_repository",
    "tuple_row_to_dict",
    "tuple_rows_to_dict",
]


def alchemy_execute_query_on_repository(repository: Repository):
    async def proxy(*args, **kwargs):
        return await repository.session().execute(*args, **kwargs)

    return proxy


def tuple_row_to_dict(row: Any):
    return dict(zip(row.keys(), row))


def tuple_rows_to_dict(rows: List[Any]):
    return [tuple_row_to_dict(row) for row in rows]
