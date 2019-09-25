import logging
import os

from olimage.utils.downloader import Downloader
from olimage.utils.builder import Builder
from olimage.packages import Package

import olimage.environment as environment

logger = logging.getLogger(__name__)


class ATF(Package):

    def __init__(self, config):

        self._name = 'arm-trusted-firmware'
        self._config = config

        self._builder = Builder(self._name, self._config)

        # Initialize callback methods
        callbacks = {
            'download': self._download,
            'configure': self._configure,
            'build':        self._build,
            'install': self._install,
        }
        super().__init__(**callbacks)

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

    def _download(self):
        Downloader(self._name, self._config).download()

    def _configure(self):
        self._builder.extract()

    def _build(self):
        self._builder.make("CROSS_COMPILE={} PLAT={} DEBUG={} {}".format(
            self._config['toolchain']['prefix'],
            self._config['platform'],
            1 if self._config['debug'] else 0,
            self._config['targets'][0]))

    def _install(self):
        # BL31 is needed for u-boot compilation
        environment.env['BL31'] = os.path.join(self._builder.paths['extract'], self._config['images'][0])
