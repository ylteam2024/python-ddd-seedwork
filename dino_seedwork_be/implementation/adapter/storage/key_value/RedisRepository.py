from typing import Optional, Union

from redis import Redis
from returns.future import future_safe
from returns.maybe import Maybe

from dino_seedwork_be.adapters.persistance.key_value.AbstractKeyValueRepository import \
    AbstractKeyValueRepository


class RedisPyRepository(AbstractKeyValueRepository):

    _redis: Redis

    def __init__(self, redis: Redis, prefix: str = "") -> None:
        self._redis = redis
        super().__init__(prefix)

    def redis(self):
        return self._redis

    def _key_with_prefix(self, key: str) -> str:
        prefix = self._prefix
        return f"{prefix}:{key}" if len(prefix) > 0 else key

    @future_safe
    async def set(
        self,
        key: str,
        value: Union[bytes, memoryview, str, int, float],
        expired_seconds: Optional[int] = None,
    ):
        return self.redis().set(
            name=self._key_with_prefix(key), value=value, ex=expired_seconds
        )

    @future_safe
    async def get(self, key: str) -> Maybe:
        return Maybe.from_optional(self.redis().get(name=self._key_with_prefix(key)))
