import logging
import shlex

from olimage.packages import Package
from olimage.utils.downloader import Downloader
from olimage.utils.builder import Builder
from olimage.utils.worker import Worker


logger = logging.getLogger(__name__)


class Linux(Package):

    def __init__(self, config):

        self._name = 'linux'
        self._config = config

        self._builder = Builder(self._name, self._config)

    @staticmethod
    def alias():
        return 'linux'

    @property
    def dependency(self):
        try:
            return self._config['depends']
        except KeyError:
            return []

    def __str__(self):
        return self._name

    def build(self):
        print("\nBuilding: \033[1m{}\033[0m".format(self))

        return self

        # Download package
        Downloader(self._name, self._config).download()

        # Build package

        self._builder.extract()
        self._builder.configure("ARCH={} {}".format(
                self._config['arch'],
                'defconfig' if self._config['defconfig'] is None else self._config['defconfig'] + '_defconfig'))
        self._builder.build("ARCH={} CROSS_COMPILE={} {}".format(
                self._config['arch'],
                self._config['toolchain']['prefix'],
                ' '.join(self._config['targets'])))

        return self

    def package(self):

        arch = self._config['arch']
        toolchain = self._config['toolchain']['prefix']

        logger.info("Building linux packages")
        self._builder.build("KBUILD_DEBARCH={} KDEB_PKGVERSION={} ARCH={} CROSS_COMPILE={} deb-pkg".format(arch, 1, arch, toolchain))

        return self



