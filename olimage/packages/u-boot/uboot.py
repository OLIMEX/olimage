import logging
import os
import shlex
import shutil

from olimage.core.parsers import Board
from olimage.packages.package import AbstractPackage
from olimage.utils import (Builder, Downloader, Templater, Worker)

import olimage.environment as env

logger = logging.getLogger(__name__)


class Uboot(AbstractPackage):
    def __init__(self, boards):

        self._name = 'u-boot'

        # Initialize dependencies
        self._board: Board = boards.get_board(env.options['board'])

        # Configure utils
        self._package = self._board.get_board_package(self._name)
        self._data = self._package.data

        self._builder = Builder(self._name, self._data)

        # Some global data
        self._pkg_version = None
        self._arch = self._board.arch
        self._binary = None
        self._package_deb = None

    @staticmethod
    def alias():
        """
        Get modules alias

        :return: string alias
        """
        return 'u-boot'

    @property
    def dependency(self):
        """
        Get package dependency:
            - arm-trusted-firmware

        :return: list with dependency packages
        """
        try:
            return self._package.depends
        except AttributeError:
            return []

    def __str__(self):
        """
        Get package name

        :return: string with name
        """
        return self._name

    def download(self):
        """
        Download u-boot sources

        1. Clone repository
        2. Create archive
        3. Extract archive to the build directory

        :return:
        """
        Downloader(self._name, self._data).download()
        self._builder.extract()

    def patch(self):
        """
        Apply patches

        :return: None
        """
        self._builder.patch(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'patches'))

    def configure(self):
        """
        Specify u-boot defconfig

        :return: None
        """
        self._builder.make("{}_defconfig".format(self._package.defconfig))

    def build(self):
        """
        Build u-boot from sources

        1. Build sources
        2. Build default env image

        :return: None
        """
        toolchain = self._package.toolchain.prefix
        path = self._builder.paths['extract']

        # Build sources
        self._builder.make("CROSS_COMPILE={}".format(toolchain))

        # Generate env
        Worker.run(
            ["CROSS_COMPILE={} {}/scripts/get_default_envs.sh > {}/uboot.env.txt".format(toolchain, path, path)],
            logger,
            shell=True
        )
        Worker.run(
            ["{}/tools/mkenvimage -s {} -o {}/uboot.env {}/uboot.env.txt".format(path, 0x20000, path, path)],
            logger,
            shell=True
        )

    def package(self):
        """
        Generate .deb file

        1. Create directory structure
        2. Copy install files
        3. Install control files
        4. Generate .deb file

        :return: None
        """
        build = self._builder.paths['build']
        package_dir = os.path.join(build, 'u-boot-sunxi')

        logger.info("Preparing build directory: {}".format(package_dir))

        # Remove packaging folder is exists
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
        os.mkdir(package_dir)

        # Generate package version
        self._pkg_version = self._builder.make("ubootversion").decode().splitlines()[1] + self._package.version

        # Install target files
        size = 0
        for f in self._package.install:
            src, dest = f.split(':')

            dest = os.path.join(package_dir, dest)

            if not os.path.exists(dest):
                os.makedirs(dest)

            logger.info("Copying {} to {}".format(src, dest))

            dest = os.path.join(dest, src)
            src = os.path.join(self._builder.paths['extract'], src)
            if 'u-boot-sunxi-with-spl.bin' in src:
                self._binary = src

            shutil.copyfile(src, dest)
            size += os.path.getsize(dest)

        # Copy overlay
        Worker.run(
            ["cp -rvf {}/overlay/* {}".format(os.path.dirname(os.path.abspath(__file__)), package_dir)],
            logger,
            shell=True)

        # Generate template files
        Templater.install(
            [
                os.path.join(package_dir, 'boot/boot.cmd')
            ],
            bootargs={
                'console': 'ttyS0,115200',
                'panic': 10,
                'loglevel': 7,
            },
            fit={
                'file': 'kernel.itb',
                'load': '0x60000000'
            },
        )

        Worker.run(
            ["mkimage -C none -A arm -T script -d {}/boot/boot.cmd {}/boot/boot.scr".format(package_dir, package_dir)],
            logger,
            shell=True)

        Templater.install(
            [
                os.path.join(package_dir, 'DEBIAN/control')
            ],
            version=self._pkg_version,
            arch=self._arch,
            size=int(size // 1024)
        )

        Templater.install(
            [
                os.path.join(package_dir, 'usr/lib/u-boot/kernel.its')
            ],
            arch=self._arch,
            fdt=self._board.variants[0].fdt,
            kernel={
                'load': '0x40080000',
                'entry': '0x40080000'
            },
            ramdisk={
                'load': '0x4FE00000',
                'entry': '0x4FE00000'
            }
        )

        Templater.install(
            [
                os.path.join(package_dir, 'usr/lib/u-boot/kernel.its')
            ],
            arch=self._arch,
            fdt=self._board.variants[0].fdt,
            kernel={
                'load': '0x40080000',
                'entry': '0x40080000'
            },
            ramdisk={
                'load': '0x4FE00000',
                'entry': '0x4FE00000'
            }
        )

        Templater.install(
            [
                os.path.join(package_dir, 'etc/kernel/postinst.d/uboot-fit')
            ],
            "755"
        )

        # Build package
        self._package_deb = 'u-boot-sunxi_{}_{}.deb'.format(self._pkg_version, self._arch)
        Worker.run(shlex.split('dpkg-deb -b {} {}'.format(package_dir, os.path.join(build, self._package_deb))), logger)

    def install(self):
        """
        Install u-boot into the target rootfs

        1. Copy .deb file
        2. Run chroot and install
        3. Remove .deb file
        4. Flash binary

        :return: None
        """

        rootfs = env.paths['rootfs']
        image = env.paths['output_file']
        build = self._builder.paths['build']

        # Copy file
        Worker.run(shlex.split('cp -vf {} {}'.format(os.path.join(build, self._package_deb), rootfs)), logger)

        # Install
        Worker.chroot(shlex.split('apt-get install -f -y ./{}'.format(self._package_deb)), rootfs, logger)

        # Remove file
        Worker.run(shlex.split('rm -vf {}'.format(os.path.join(rootfs, self._package_deb))), logger)

        # Flash
        if self._binary:
            Worker.run(shlex.split('dd if={} of={} conv=notrunc,fsync bs=1k seek=8'.format(
                self._binary, image)), logger)
