from .parser import GenericLoader


class Repository(object):
    def __init__(self, name: str, data: dict) -> None:
        self._name = name
        self._data = data

    def __str__(self) -> str:
        return self._name

    @property
    def components(self) -> list:
        print(self._data)
        import sys
        sys.exit(0)


class Repositories(GenericLoader):
    def __init__(self) -> None:
        super().__init__("repositories", Repository)

