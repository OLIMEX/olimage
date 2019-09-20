import logging

from utils.downloader import Downloader
from utils.builder import Builder
from utils.packager import Packager

import bsp

logger = logging.getLogger(__name__)


class Uboot(bsp.BSP):

    def __init__(self, config, **kwargs):

        self._name = 'u-boot'
        self._config = config[self._name]
        self._workdir = kwargs['workdir']

    @staticmethod
    def alias():
        return 'u-boot'

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

        p = Packager(self._name, self._workdir, self._config)
        p.prepare(version='2019.07+olimex-1')
        return

        # Download package
        Downloader(self._name, self._workdir, self._config).download()

        # Build package
        Builder(self._name, self._workdir, self._config)\
            .extract()\
            .configure("{}_defconfig".format(self._config['defconfig']))\
            .build("CROSS_COMPILE={}".format(self._config['toolchain']['prefix']))

        # Generate deb
        p = Packager(self._name, self._workdir, self._config)

