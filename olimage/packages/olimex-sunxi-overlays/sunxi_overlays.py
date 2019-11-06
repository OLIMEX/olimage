import logging
import os
import shlex


from olimage.core.stamp import stamp
from olimage.core.utils import Utils
from olimage.packages.package import AbstractPackage
from olimage.utils import (Builder, Downloader, Worker)

import olimage.environment as env


class OlimexSunxiOverlays(AbstractPackage):
    def __init__(self, boards):

        self._name = 'olimex-sunxi-overlays'
        super().__init__(boards)

    @staticmethod
    def alias():
        """
        Get modules alias

        :return: string alias
        """
        return 'olimex-sunxi-overlays'

    @property
    def deb(self) -> str:
        return "olimex-sunxi-overlays_1.0.0_all.deb"

    def package(self):
        """
        Generate .deb file

        :return: None
        """

        # Build package
        # This command returns error since target and host arch doesn't match. We are using only the generated .deb
        # file, so ignore the error for now.
        Worker.run(
            ['cd {} && debuild -us -uc'.format(self._builder.paths['extract'])],
            self.logger,
            shell=True,
            ignore_fail=True,
            log_error=False
        )
