import logging
import os

from olimage.core.parsers import Board
from olimage.packages.package import AbstractPackage
from olimage.utils import Downloader, Builder

import olimage.environment as env

logger = logging.getLogger(__name__)


class ATF(AbstractPackage):

    def __init__(self, boards):

        self._name = 'arm-trusted-firmware'

        # Initialize dependencies
        self._board: Board = boards.get_board(env.options['board'])

        # Configure utils
        self._package = self._board.get_board_package(self._name)
        self._data = self._package.data

        self._builder = Builder(self._name, self._data)

    @staticmethod
    def alias():
        return "arm-trusted-firmware"

    @property
    def dependency(self):
        try:
            return self._package.depends
        except AttributeError:
            return []

    def __str__(self):
        return self._name

    def download(self):
        Downloader(self._name, self._data).download()

    def patch(self):
        pass

    def configure(self):
        self._builder.extract()

    def build(self):
        self._builder.make("CROSS_COMPILE={} PLAT={} DEBUG={} {}".format(
            self._package.toolchain.prefix,
            self._package.platform,
            1 if self._package.debug else 0,
            self._package.targets[0]))

    def package(self):
        pass

    def install(self):
        # BL31 is needed for u-boot compilation
        env.env['BL31'] = os.path.join(self._builder.paths['extract'], self._package.images[0])
