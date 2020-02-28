import abc

from olimage.core.parsers import ParserPackages, ParserException
from olimage.core.parsers.packages.service import Service


class SetupAbstract(object):
    def __init__(self):
        try:
            self._parser = ParserPackages().get_service(self.__module__)
        except ParserException:
            self._parser = None

    @property
    def packages(self) -> list:
        if self._parser:
            return self._parser.packages
        return []

    @property
    def parser(self) -> Service:
        return self._parser

    @abc.abstractmethod
    def setup(self, *args, **kwargs):
        pass
