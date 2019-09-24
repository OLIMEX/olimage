import logging

from olimage.utils.downloader import Downloader
from olimage.utils.builder import Builder
from olimage.packages import Package

logger = logging.getLogger(__name__)


class Linux(Package):

    def __init__(self, config):

        self._name = 'linux'
        self._config = config

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

        # Download package
        Downloader(self._name, self._config).download()

        # Build package
        b = Builder(self._name, self._config)
        b.extract()
        b.configure("ARCH={} {}".format(
                self._config['arch'],
                'defconfig' if self._config['defconfig'] is None else self._config['defconfig'] + '_defconfig'))
        b.build("ARCH={} CROSS_COMPILE={} {}".format(
                self._config['arch'],
                self._config['toolchain']['prefix'],
                ' '.join(self._config['targets'])))

        # Generate deb

