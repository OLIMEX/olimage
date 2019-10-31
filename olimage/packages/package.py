import abc
import logging
import os

import olimage.environment as env

from olimage.utils import Printer
from olimage.core.parsers import Board
from olimage.core.stamp import stamp
from olimage.core.utils import Utils
from olimage.utils import Builder


class PackageException(Exception):
    pass


class AbstractPackage(metaclass=abc.ABCMeta):
    """
    Package base class

    This class is abstract, interface like
    """
    def __init__(self, boards):

        # Initialize dependencies
        self._board: Board = boards.get_board(env.options['board'])

        # Configure utils
        self._package = self._board.get_board_package(self._name)
        self._data = self._package.data

        # Configure paths
        workdir = env.paths['workdir']
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), self._name)
        self.paths = {
            # Package directories
            'patches': os.path.join(base, 'patches'),
            'fragments': os.path.join(base, 'fragments'),
            'overlay': os.path.join(base, 'overlay'),

            # Download directories/files
            'download': os.path.join(workdir, 'dl', self._name),
            'archive': os.path.join(workdir, 'dl', self._name, self._data['refs'] + '.tar.gz'),

            # Build directories/files
            'build': os.path.join(workdir, 'build', self._name),
            'compile': os.path.join(workdir, 'build', self._name, self._data['refs']),
        }

        # Check if paths exists
        for path in ['download', 'build']:
            if not os.path.exists(self.paths[path]):
                os.mkdir(self.paths[path])

        self._builder = Builder(self._name, self._data)

        # Initialize logger. Use "olimage.package"  + package alias
        self.logger = logging.getLogger(".".join(str(__name__).split('.')[:-1] + [str(self)]))

    def __str__(self) -> str:
        """
        Get package name

        :return: string with name
        """
        return self._name

    @classmethod
    @abc.abstractmethod
    def alias(cls):
        """
        Get class alias

        This is useful, when searching for class name

        :return: string
        """
        pass

    @property
    def dependency(self):
        """
        Get package dependency

        :return: list with dependency packages
        """
        try:
            return self._package.depends
        except AttributeError:
            return []

    @stamp
    def download(self) -> None:
        """
        Download package

        :return: None
        """
        # Clone and compress sources
        dl = Utils.download.git(self._data['source'], self.paths['download'], ref=self._data['refs'])
        Utils.archive.gzip(dl, self.paths['archive'])

        # Extract them to build directory
        Utils.archive.extract(self.paths['archive'], self.paths['build'])

    @stamp
    def patch(self) -> None:
        """
        Apply patches

        :return: None
        """
        Utils.patch.apply(self.paths['patches'], self.paths['compile'])

    def configure(self) -> None:
        """
        Configure package

        :return: None
        """
        pass

    def build(self) -> None:
        """
        Build package

        :return: None
        """
        pass

    def package(self) -> None:
        """
        Make debian package

        :return: None
        """
        pass

    def install(self) -> None:
        """
        Install package

        :return: None
        """
        pass


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
