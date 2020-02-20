import abc

from olimage.core.parsers import ParserPackages


class SetupAbstract(object):
    def __init__(self):
        pass

    @property
    def packages(self) -> list:
        return ParserPackages().get_service(self.__module__).packages

    @abc.abstractmethod
    def setup(self, *args, **kwargs):
        pass
