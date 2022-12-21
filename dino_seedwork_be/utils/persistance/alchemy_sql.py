from typing import Any, List

from dino_seedwork_be.adapters import Repository


def alchemy_execute_query_on_repostory(repository: Repository):
    async def proxy(*args, **kwargs):
        return await repository.session().execute(*args, **kwargs)

    return proxy


def tuple_row_to_dict(row: Any):
    return dict(zip(row.keys(), row))


def tuple_rows_to_dict(rows: List[Any]):
    return [tuple_row_to_dict(row) for row in rows]
