import validators
from returns.maybe import Some

from dino_seedwork_be.domain.value_object.AbstractValueObject import \
    ValueObject
from dino_seedwork_be.utils.validator import is_url_image

# __all__ = ["ImageURL"]


class ImageURL(ValueObject):
    _url: str

    def __init__(self, url: str, validate_url: bool = False):
        self.set_url(url, validate_url)
        super().__init__()

    def set_url(self, url: str, validate_url: bool = False):
        self.assert_argument_not_empty(
            Some(url), a_message=Some("url string cannot be None")
        ).unwrap()
        validators.url(url)
        if validate_url:
            self.assert_state_true(
                is_url_image(url), Some("url is not a valid url image")
            ).unwrap()
        self._url = url

    def url(self) -> str:
        return self._url
