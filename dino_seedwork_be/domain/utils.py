from returns.maybe import Maybe

from dino_seedwork_be.domain.Entity import Entity, RawAttributes
from dino_seedwork_be.domain.IdentifiedDomainObject import IdentityType
from dino_seedwork_be.utils.functional import print_exception_with_traceback

from .exceptions import DomainException

# __all__ = ["get_identity", "get_raw_identity"]


def get_identity(an_entity: Entity[RawAttributes, IdentityType]) -> Maybe[IdentityType]:
    return an_entity.identity()


def get_raw_identity(an_entity: Entity) -> Maybe[str]:
    return an_entity.id_as_string()


def exception_to_domain_exception(code: str, prefix: str, exception: Exception):
    return DomainException(
        code=code,
        message=f"[{prefix} - {str(exception)}] {print_exception_with_traceback(exception)}",
    )
