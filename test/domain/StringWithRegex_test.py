import pytest
from returns.maybe import Some

from dino_seedwork_be.domain.value_object.RegexValue import StringWithRegex


class TestStringWithRegex:
    def test_work_normally(self):
        url_regex = StringWithRegex(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
            "URL_NOT_IN_VALID_FORMAT",
        )
        url_regex.set_value(Some("http://google.com")).unwrap()
        assert url_regex.value() == "http://google.com"

        with pytest.raises(Exception):
            url_regex.set_value(Some("invalid_url_here")).unwrap()
