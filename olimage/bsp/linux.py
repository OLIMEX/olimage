import logging

from utils.downloader import Downloader
from utils.builder import Builder

import bsp

logger = logging.getLogger(__name__)


class Kernel(bsp.BSP):

    def __init__(self, config, **kwargs):

        self._name = 'linux'

        self._config = config[self._name]
        self._workdir = kwargs['workdir']

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
        Downloader(self._name, self._workdir, self._config).download()

        # Build package
        Builder(self._name, self._workdir, self._config)\
            .extract()\
            .configure("ARCH={} {}".format(
                self._config['arch'],
                'defconfig' if self._config['defconfig'] is None else self._config['defconfig'] + '_defconfig'))\
            .build("ARCH={} CROSS_COMPILE={} {}".format(
                self._config['arch'],
                self._config['toolchain']['prefix'],
                ' '.join(self._config['targets'])))

        # Generate deb

