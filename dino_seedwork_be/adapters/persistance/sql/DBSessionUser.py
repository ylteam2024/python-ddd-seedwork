from typing import Generic, List, TypeVar

from dino_seedwork_be.utils.functional import for_each

SessionType = TypeVar("SessionType")


class SessionUserAlreadyHaveSession(Exception):
    ...


class DBSessionUser(Generic[SessionType]):
    _session: SessionType
    _session_preserved = False

    def session(self) -> SessionType:
        return self._session

    def set_session_preserved(self, aBool: bool):
        self._session_preserved = aBool

    def _set_ession(self, session: SessionType):
        self._session = session

    def set_session(self, session: SessionType):
        try:
            if self.session() is not None and not self.is_current_session_closed():
                if not self._session_preserved:
                    raise SessionUserAlreadyHaveSession(
                        f" {str(self)} already ocuppied by a session"
                    )
        except AttributeError:
            self._set_ession(session)
        self._set_ession(session)

    def is_current_session_closed(self) -> bool:
        session = self.session()
        return not (session.new or session.dirty or session.deleted)


class SuperDBSessionUser(Generic[SessionType], DBSessionUser[SessionType]):
    _session_users: List[DBSessionUser] = []
    _session: SessionType

    def set_session(self, session: SessionType):
        self._session = session
        if self.session_users() is not None:
            for_each(
                lambda sessionUser, _: sessionUser.set_session(session),
                self.session_users(),
            )

    def session(self):
        return self._session

    def session_users(self) -> List[DBSessionUser]:
        return self._session_users

    def set_session_users(self, session_users: List[DBSessionUser]):
        self._session_users = session_users
