from typing import Any, List
from src.seedwork.adapters.repository import Repository


def alchemyExecuteQueryOnRepostory(repository: Repository):
    async def proxy(*args, **kwargs):
        return await repository.getSession().execute(*args, **kwargs)

    return proxy

def tupleRowToDict(row: Any):
    return dict(zip(row.keys(), row))

def tupleRowsToDict(rows: List[Any]):
    return [tupleRowToDict(row) for row in rows]
