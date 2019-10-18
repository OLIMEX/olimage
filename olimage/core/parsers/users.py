from .parser import GenericLoader


class User(object):
    def __init__(self, name: str, data: dict) -> None:
        self._name = name
        self._data = data

    def __str__(self):
        return self._name

    @property
    def password(self):
        return self._data['password']

    @property
    def groups(self):
        try:
            return self._data['groups']
        except KeyError:
            return []

    @property
    def force_change(self):
        try:
            return self._data['force_change']
        except KeyError:
            return False

    @property
    def permit_login(self):
        try:
            return self._data['permit_login']
        except KeyError:
            return False


class Users(GenericLoader):
    def __init__(self) -> None:
        super().__init__("users", User)

