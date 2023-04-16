from dino_seedwork_be.domain.Entity import Entity, RawAttributes
from dino_seedwork_be.domain.IdentifiedDomainObject import IdentityType
from dino_seedwork_be.utils.functional import print_exception_with_traceback

from .exceptions import DomainException

__all__ = ["get_identity", "get_raw_identity"]


def get_identity(aEntity: Entity[RawAttributes, IdentityType]) -> IdentityType:
    return aEntity.identity()


def get_raw_identity(aEntity: Entity) -> str:
    return aEntity.id_as_string()


def exception_to_domain_exception(code: str, prefix: str, exception: Exception):
    return DomainException(
        code=code,
        message=f"[{prefix} - {str(exception)}] {print_exception_with_traceback(exception)}",
    )
