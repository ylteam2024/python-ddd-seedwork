from typing import List, Optional, TypeVar

from faker import Faker
from returns.pipeline import flow

fake = Faker()
Faker.seed(0)  # This will raise a TypeError

ElementType = TypeVar("ElementType")


def random_elements_or_none(elements: List[ElementType]) -> Optional[List[ElementType]]:
    return flow(
        tuple(elements),
        lambda elements: fake.random_elements(elements=elements, unique=True),
        lambda v: (v, None),
        fake.random_element,
    )


def random_element_or_none(element: ElementType) -> Optional[ElementType]:
    return fake.random_element(elements=(element, None))
