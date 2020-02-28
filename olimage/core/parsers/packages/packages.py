import olimage.environment as env

from olimage.core.parsers.parser import GenericLoader
from olimage.core.parsers import ParserException

from .release import Release
from .service import Service
from .variant import Variant


class ParserPackages(object):
    def __init__(self) -> None:
        self._releases = GenericLoader("releases", Release, path=env.paths['configs'] + '/core/packages.yaml')
        self._services = GenericLoader("services", Service, path=env.paths['configs'] + '/core/packages.yaml')
        self._variants = GenericLoader("variants", Variant, path=env.paths['configs'] + '/core/packages.yaml')

    @property
    def releases(self):
        return list(self._releases)

    @property
    def services(self):
        return list(self._services)

    @property
    def variants(self):
        return list(self._variants)

    def get_release(self, name: str) -> Release:
        """
        Get release packages

        :param name: release name
        :return: Release object or None if there are no release packages
        """
        for release in self._releases:
            if name.lower() == str(release).lower():
                return release

        return None

    def get_service(self, name: str) -> Service:
        """
        Get service packages

        :param name: service name
        :return: Service object
        """
        for service in self._services:
            if name.lower() == str(service).lower():
                return service

        raise ParserException("Service not found: \'{}\'".format(name))

    def get_variant(self, name: str) -> Variant:
        """
        Get variant packages

        :param name: variant name, e.g. lite, base, full, etc...
        :return: Variant object
        """
        for variant in self._variants:
            if name.lower() == str(variant).lower():
                return variant

        raise ParserException("Variant not found: \'{}\'".format(name))


