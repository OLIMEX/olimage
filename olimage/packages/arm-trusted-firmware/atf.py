import logging

from olimage.utils.downloader import Downloader
from olimage.utils.builder import Builder
from olimage.packages import Package

import olimage.environment as environment

logger = logging.getLogger(__name__)


class ATF(Package):

    def __init__(self, config):

        self._name = 'arm-trusted-firmware'
        self._config = config

    @staticmethod
    def alias():
        return "arm-trusted-firmware"

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
        b.configure()
        b.build("CROSS_COMPILE={} PLAT={} DEBUG={} {}".format(
            self._config['toolchain']['prefix'],
            self._config['platform'],
            1 if self._config['debug'] else 0,
            self._config['targets'][0]))

        # BL31 is needed for u-boot compilation
        environment.env['BL31'] = b.paths['extract'] + '/' + self._config['images'][0]
