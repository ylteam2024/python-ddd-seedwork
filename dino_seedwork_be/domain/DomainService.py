from typing import Optional

from dino_seedwork_be.storage.uow import SuperDBSessionUser

from .DomainEventPublisher import DomainEventPublisher
from .mixins import BusinessRuleValidationMixin

__all__ = ["DomainService"]


class DomainService(BusinessRuleValidationMixin, SuperDBSessionUser):
    """
    Domain services carry domain knowledge that doesnt naturally fit entities and value objects.
    """

    _domain_event_publisher: DomainEventPublisher | None

    def __init__(
        self,
        domain_event_publisher: Optional[DomainEventPublisher] = None,
    ) -> None:
        self._domain_event_publisher = domain_event_publisher
        super().__init__()

    def domain_event_publisher(self) -> DomainEventPublisher:
        return self._domain_event_publisher or DomainEventPublisher.instance()
