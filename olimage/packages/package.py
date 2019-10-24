import abc
import functools

import olimage.environment as env

from olimage.utils import Printer
from olimage.core.parsers import (Board, Partitions)
from olimage.utils import (Builder, PackageStamper)


class PackageException(Exception):
    pass


class AbstractPackage(metaclass=abc.ABCMeta):
    """
    Package base class

    This class is abstract, interface like
    """

    def __init__(self, boards, partitions):

        # Initialize dependencies
        self._board: Board = boards.get_board(env.options['board'])
        self._partitions: Partitions = partitions

        # Configure utils
        self._package = self._board.get_board_package(self._name)
        self._data = self._package.data

        self._builder = Builder(self._name, self._data)

        self.stamper = PackageStamper(self._builder.paths['build'])

    # def stamp(func):
        # def wrapper(self: AbstractPackage, *args, **kwargs):
        #     self.stamper.stamp(func.__name__)
        #     return func(self, *args, **kwargs)
        #
        # return wrapper


    @abc.abstractclassmethod
    def alias(cls):
        """
        Get class alias

        This is useful, when searching for class name

        :return: string
        """
        pass

    @abc.abstractmethod
    def dependency(self):
        """
        Get package dependency

        :return: list
        """
        pass

    @abc.abstractmethod
    def download(self):
        """
        Download package

        :return: None
        """
        pass

    @abc.abstractmethod
    def patch(self):
        """
        Apply patches

        :return: None
        """
        pass

    @abc.abstractmethod
    def configure(self):
        """
        Configure package

        :return: None
        """
        pass

    @abc.abstractmethod
    def build(self):
        """
        Build package

        :return: None
        """
        pass

    @abc.abstractmethod
    def package(self):
        """
        Make debian package

        :return: None
        """
        pass

    @abc.abstractmethod
    def install(self):
        """
        Install package

        :return: None
        """
        pass


# class PackageBase(AbstractPackage):
#
#     def __str__(self) -> str:
#         return self._name
#
#     @staticmethod
#     def alias():
#         pass
#
#     @property
#     def dependency(self):
#         pass
#
#     def download(self):
#         pass
#
#     def patch(self):
#         pass
#
#     def configure(self):
#         pass
#
#     def build(self):
#         pass
#
#     def package(self):
#         pass
#
#     def install(self):
#         pass


class Packages(object):
    def __init__(self, packages: dict):
        """
        Worker class for packages

        :param packages: dict|list
        """

        self._packages = packages
        self._ordered_packages = Packages.resolve_dependencies(packages)

    @staticmethod
    def resolve_dependencies(packages):

        # Convert dict to list
        if isinstance(packages, dict):
            items = [{key:value} for key,value in packages.items()]
        elif isinstance(packages, list):
            items = packages
        else:
            raise PackageException("Packages must be list or dict")

        order = []
        provided = set()
        while items:
            remaining_items = []
            emitted = False

            for item in items:
                for key,value in item.items():
                    dependencies = set(value.dependency)

                    if dependencies.issubset(provided):
                        order.append(item)
                        provided.add(key)
                        emitted = True
                    else:
                        remaining_items.append(item)

            if not emitted:
                raise Exception("Failed to resolve dependencies")

            items = remaining_items

        return order

    def _check_package(self, package):
        if package not in self._packages:
            raise PackageException("Unknown package \'{}\'".format(package))

    def run(self, package, command):
        chain = ['download', 'patch', 'configure', 'build', 'package', 'install']

        # Check if package exists
        self._check_package(package)

        # Execute chain
        for c in chain:
            getattr(self, c)(package)
            if command == c:
                break

    @property
    def packages(self) -> list:
        return self._ordered_packages

    @Printer("Downloading")
    def download(self, package):
        self._packages[package].download()

    @Printer("Patching")
    def patch(self, package):
        self._packages[package].patch()

    @Printer("Configuring")
    def configure(self, package):
        self._packages[package].configure()

    @Printer("Building")
    def build(self, package):
        self._packages[package].build()

    @Printer("Packaging")
    def package(self, package):
        self._packages[package].package()

    @Printer("Installing")
    def install(self, package):
        self._packages[package].install()
