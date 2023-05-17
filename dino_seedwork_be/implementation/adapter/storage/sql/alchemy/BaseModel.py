from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID

__all__ = ["UUIDBaseModel"]


class UUIDBaseModel:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
