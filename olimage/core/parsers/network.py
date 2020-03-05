import olimage.environment as env

from .exceptions import ParserException
from .parser import GenericLoader


class Interface(object):
    def __init__(self, name: str, data: dict) -> None:
        self._name = name
        self._data = data

    def __str__(self) -> str:
        return self._name

    @property
    def auto(self) -> bool:
        """
        Get if interface should be auto raised

        :return: boolean
        """
        if 'auto' in self._data:
            return self._data['auto']

        raise ParserException("\'auto\' not defined!")

    @property
    def allow_hotplug(self) -> bool:
        """
        Should the interface be hot-plugged

        :return: boolean
        """
        if 'allow_hotplug' in self._data:
            return self._data['allow_hotplug']

        raise ParserException("\'allow_hotplug\' not defined!")

    @property
    def dhcp(self) -> bool:
        """
        Should the interface be configured by DHCP

        :return: boolean
        """
        if 'dhcp' in self._data:
            return self._data['dhcp']

        raise ParserException("\'dhcp\' not defined!")


class NetworkParser(GenericLoader):
    def __init__(self) -> None:
        self._interfaces = GenericLoader("interfaces", Interface, path=env.paths['configs'] + '/network.yaml')

    @property
    def interfaces(self) -> list:
        return list(self._interfaces)

