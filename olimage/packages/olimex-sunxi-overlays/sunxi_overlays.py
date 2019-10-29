import logging
import os
import shlex


from olimage.core.stamp import stamp
from olimage.core.utils import Utils
from olimage.packages.package import AbstractPackage
from olimage.utils import (Builder, Downloader, Worker)

import olimage.environment as env

logger = logging.getLogger(__name__)


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

    @stamp
    def download(self):
        """
        Download u-boot sources

        1. Clone repository
        2. Create archive
        3. Extract archive to the build directory

        :return:
        """
        Downloader(self._name, self._data).download()
        Utils.archive.extract(self._path['archive'], self._path['build'])

    def patch(self):
        pass

    def configure(self):
        pass

    def build(self):
        pass

    def package(self):
        """
        Generate .deb file

        :return: None
        """

        # Build package
        # This command returns error since target and host arch doesn't match. We are using only the generated .deb
        # file, so ignore the error for now.
        Worker.run(
            ['cd {} && debuild -us -uc -a {}'.format(self._builder.paths['extract'], self._data['arch'])],
            logger,
            shell=True,
            ignore_fail=True,
            log_error=False
        )

    def install(self):
        """
        Install package into the target rootfs

        1. Copy .deb file
        2. Run chroot and install
        3. Remove .deb file

        :return: None
        """
        rootfs = env.paths['rootfs']
        build = self._builder.paths['build']

        # Copy file
        Worker.run(shlex.split('cp -vf {} {}'.format(os.path.join(build, "olimex-sunxi-overlays_1.0.0_arm64.deb"), rootfs)), logger)

        # Install
        Worker.chroot(shlex.split('apt-get install -f -y ./{}'.format("olimex-sunxi-overlays_1.0.0_arm64.deb")), rootfs, logger)

        # Remove file
        Worker.run(shlex.split('rm -vf {}'.format(os.path.join(rootfs, "olimex-sunxi-overlays_1.0.0_arm64.deb"))), logger)
