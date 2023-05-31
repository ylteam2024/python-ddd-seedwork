from returns.maybe import Maybe, Nothing, Some

from .DomainEventPublisher import DomainEventPublisher

# __all__ = ["DomainService"]


class DomainService:
    """
    Domain services carry domain knowledge that doesnt naturally fit entities and value objects.
    """

    _domain_event_publisher: DomainEventPublisher

    def __init__(
        self,
        domain_event_publisher: Maybe[DomainEventPublisher] = Nothing,
    ) -> None:
        match domain_event_publisher:
            case Some(instance):
                self._domain_event_publisher = instance
            case Maybe.empty:
                self._domain_event_publisher = DomainEventPublisher.instance()
        super().__init__()

    def domain_event_publisher(self) -> DomainEventPublisher:
        return self._domain_event_publisher
