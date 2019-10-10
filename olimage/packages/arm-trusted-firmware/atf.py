import logging
import os

from olimage.packages.package import PackageBase
from olimage.utils import Downloader, Builder

import olimage.environment as environment

logger = logging.getLogger(__name__)


class ATF(PackageBase):

    def __init__(self, config):

        self._name = 'arm-trusted-firmware'
        self._config = config

        self._builder = Builder(self._name, self._config)

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

    def download(self):
        Downloader(self._name, self._config).download()

    def configure(self):
        self._builder.extract()

    def build(self):
        self._builder.make("CROSS_COMPILE={} PLAT={} DEBUG={} {}".format(
            self._config['toolchain']['prefix'],
            self._config['platform'],
            1 if self._config['debug'] else 0,
            self._config['targets'][0]))

    def package(self):
        pass

    def install(self):
        # BL31 is needed for u-boot compilation
        environment.env['BL31'] = os.path.join(self._builder.paths['extract'], self._config['images'][0])
