from typing import Optional

from pika.credentials import PlainCredentials
from returns.maybe import Maybe, Nothing, Some


class ConnectionSettings:
    _host_name: str
    _port: Optional[int]
    _username: Optional[str]
    _password: Optional[str]

    # My virtualHost, which is the name of the RabbitMQ virtual host
    _virtual_host: str

    def __init__(
        self,
        a_host_name: str,
        a_port: int,
        a_virtual_host: str,
        an_username: Optional[str],
        a_password: Optional[str],
    ) -> None:
        self._host_name = a_host_name
        self._password = a_password
        self._port = a_port
        self._username = an_username
        self._virtual_host = a_virtual_host

    def host_name(self) -> str:
        return self._host_name

    def password(self) -> Maybe[str]:
        return Maybe.from_optional(self._password)

    def port(self) -> Maybe[int]:
        return Maybe.from_optional(self._port)

    def username(self) -> Maybe[str]:
        return Maybe.from_optional(self._username)

    def virtual_host(self) -> str:
        return self._virtual_host

    @staticmethod
    def factory(a_host_name, a_port, a_virtual_host, an_username, a_password):
        return ConnectionSettings(
            a_host_name=a_host_name,
            a_port=a_port,
            a_virtual_host=a_virtual_host,
            an_username=an_username,
            a_password=a_password,
        )

    def has_user_credentials(self):
        match [self.password(), self.username()]:
            case [Some(), Some()]:
                return True
            case _:
                return False

    def get_credential(self) -> Maybe[PlainCredentials]:
        match [self.password(), self.username()]:
            case [Some(), Some()]:
                return Some(
                    PlainCredentials(
                        username=self.username().unwrap(),
                        password=self.password().unwrap(),
                    )
                )
            case _:
                return Nothing
