import abc

from olimage.core.parsers import ServicesParser, ServiceParser, ParserException


class SetupAbstract(object):
    def __init__(self):
        try:
            self._parser = ServicesParser().get(self.__module__)
        except ParserException:
            self._parser = None

    @property
    def packages(self) -> list:
        if self._parser:
            return self._parser.packages
        return []

    @property
    def parser(self) -> ServiceParser:
        return self._parser

    @abc.abstractmethod
    def setup(self, *args, **kwargs):
        pass
