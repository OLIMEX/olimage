import abc

from olimage.core.parsers import ParserPackages
from olimage.core.parsers.packages.service import Service


class SetupAbstract(object):
    def __init__(self):
        self._parser = ParserPackages().get_service(self.__module__)

    @property
    def packages(self) -> list:
        return self._parser.packages

    @property
    def parser(self) -> Service:
        return self._parser

    @abc.abstractmethod
    def setup(self, *args, **kwargs):
        pass
