from .parser import GenericLoader


class Distribution(object):
    def __init__(self, name: str, data: dict) -> None:
        self._name = name
        self._data = data

    def __str__(self) -> str:
        return self._name

    @property
    def components(self) -> list:
        return self._data['components']

    @property
    def recommended(self) -> str:
        return self._data['recommended']

    @property
    def releases(self) -> list:
        return self._data['releases']

    @property
    def repository(self) -> str:
        return self._data['repository']


class Distributions(GenericLoader):
    def __init__(self) -> None:
        super().__init__("distributions", Distribution)

