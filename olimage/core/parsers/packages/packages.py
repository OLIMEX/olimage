import olimage.environment as env

from olimage.core.parsers.parser import GenericLoader

from .service import Service
from .variant import Variant


class ParserPackages(object):
    def __init__(self) -> None:
        self._services = GenericLoader("services", Service, path=env.paths['configs'] + '/core/packages.yaml')
        self._variants = GenericLoader("variants", Variant, path=env.paths['configs'] + '/core/packages.yaml')

    @property
    def services(self):
        return list(self._services)

    @property
    def variants(self):
        return list(self._variants)

    def get_service(self, name: str) -> Service:
        """
        Get service packages

        :param name: service name
        :return: Service object
        """
        for service in self._services:
            if name.lower() == str(service).lower():
                return service

        raise Exception("Service not found: \'{}\'".format(name))

    def get_variant(self, name: str) -> Variant:
        """
        Get variant packages

        :param name: variant name, e.g. lite, base, full, etc...
        :return: Variant object
        """
        for variant in self._variants:
            if name.lower() == str(variant).lower():
                return variant

        raise Exception("Variant not found: \'{}\'".format(name))


