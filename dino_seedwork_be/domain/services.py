from src.seedwork.storage.uow import SuperDBSessionUser

from .mixins import BusinessRuleValidationMixin


class DomainService(BusinessRuleValidationMixin, SuperDBSessionUser):
    """
    Domain services carry domain knowledge that doesnt naturally fit entities and value objects.
    """
