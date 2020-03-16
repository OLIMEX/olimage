from .parser import GenericLoader


class Repository(object):
    def __init__(self, name: str, data: dict) -> None:
        self._name = name
        self._data = data

    def __str__(self) -> str:
        return self._name

    @property
    def testing(self) -> bool:
        if 'testing' in self._data:
            return self._data['testing']
        return False

    @property
    def components(self) -> list:
        if 'components' in self._data:
            return self._data['components']
        return ['main']

    @property
    def key(self) -> str:
        if 'key' in self._data:
            return self._data['key']
        return None

    @property
    def keyfile(self) -> str:
        if 'keyfile' in self._data:
            return self._data['keyfile']
        return None

    @property
    def keyserver(self) -> str:
        if 'keyserver' in self._data:
            return self._data['keyserver']
        return None

    @property
    def sources(self) -> bool:
        if 'sources' in self._data:
            return self._data['sources']
        return False

    @property
    def url(self) -> str:
        return self._data['url']


class Repositories(GenericLoader):
    def __init__(self) -> None:
        super().__init__("repositories", Repository)

