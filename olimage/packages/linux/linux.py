import logging
import shlex
import os

from olimage.core.parsers import Board
from olimage.packages.package import AbstractPackage
from olimage.utils import (Builder, Downloader, Worker)

import olimage.environment as env

logger = logging.getLogger(__name__)


class Linux(AbstractPackage):

    def __init__(self, boards):

        self._name = 'linux'

        # Initialize dependencies
        self._board: Board = boards.get_board(env.options['board'])

        # Configure utils
        self._package = self._board.get_board_package(self._name)
        self._data = self._package.data

        self._builder = Builder(self._name, self._data)

        # Some global data
        self._arch = self._board.arch
        self._toolchain = self._package.toolchain.prefix
        self._version = None

    @staticmethod
    def alias():
        return 'linux'

    @property
    def dependency(self):
        try:
            return self._package.depends
        except AttributeError:
            return []

    def __str__(self):
        return self._name

    def download(self):
        """
        Download sources. Currently only git is supported

        :return: None
        """
        Downloader(self._name, self._data).download()
        self._builder.extract()

    def configure(self):
        """
        Configure sources using defconfig

        :return: None
        """

        defconfig = 'defconfig'

        if self._package.defconfig is not None:
            defconfig = self._package.defconfig + '_defconfig'

        # Make defconfig
        self._builder.make("ARCH={} {}".format(self._arch, defconfig))

        # Apply fragments
        path = self._builder.paths['extract']
        script = os.path.join(path, 'scripts/kconfig/merge_config.sh')
        config = os.path.join(path, '.config')


        fragment = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fragments/test.fragment')

        # First merge config files
        Worker.run(shlex.split("/bin/bash -c '{} -m {} {}'".format(script, config, fragment)))

        # Second, regenerate config file
        self._builder.make("ARCH={} oldconfig".format(self._arch))

    def build(self):
        self._builder.make("ARCH={} CROSS_COMPILE={} {}".format(self._arch,self._toolchain,' '.join(self._package.targets)))

    def package(self):
        """
        Package linux kernel

        :return: None
        """
        self._version = self._builder.make("kernelversion").decode().splitlines()[1]
        self._builder.make("KDEB_PKGVERSION={}-1-olimex LOCALVERSION=-1-olimex ARCH={} CROSS_COMPILE={} bindeb-pkg".format(self._version, self._arch, self._toolchain))

    def install(self):
        """
        Install u-boot into the target rootfs

        1. Copy .deb file
        2. Run chroot and install
        3. Remove .deb file
        4. Flash binary

        :return: None
        """
        #
        rootfs = env.paths['rootfs']
        build = self._builder.paths['build']

        # Copy file
        Worker.run(shlex.split('cp -vf {} {}'.format(os.path.join(build, 'linux-image-5.3.1-1-olimex_5.3.1-1-olimex_arm64.deb'), rootfs)), logger)

        # Install
        Worker.chroot(shlex.split('dpkg -i {}'.format(os.path.basename('linux-image-5.3.1-1-olimex_5.3.1-1-olimex_arm64.deb'))), rootfs, logger)

        # Remove file
        Worker.run(shlex.split('rm -vf {}'.format(os.path.join(rootfs, 'linux-image-5.3.1-1-olimex_5.3.1-1-olimex_arm64.deb'))), logger)

