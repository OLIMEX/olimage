import olimage.environment as env

from .exceptions import ParserException
from .parser import GenericLoader


class ServiceParser(object):
    def __init__(self, name: str, data: dict) -> None:
        self._name = name
        self._data = data

    def __str__(self) -> str:
        return self._name

    def __getattr__(self, item):
        if item in self._data:
            return self._data[item]

        return super().__getattribute__(item)


class ServicesParser(GenericLoader):
    def __init__(self) -> None:
        super().__init__("services", ServiceParser, path=env.paths['configs'] + '/core/services.yaml')

    def get(self, name: str) -> ServiceParser:
        for service in self._objects:
            if name.lower() == str(service).lower():
                return service

        raise ParserException("Service not found: \'{}\'".format(name))

