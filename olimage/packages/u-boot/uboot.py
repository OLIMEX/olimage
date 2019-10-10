import logging
import os
import shlex
import shutil

from olimage.packages.package import PackageBase
from olimage.utils import (Builder, Downloader, Templater, Worker)

import olimage.environment as environment

logger = logging.getLogger(__name__)


class Uboot(PackageBase):

    def __init__(self, config):

        self._name = 'u-boot'
        self._config = config

        # Configure builder
        self._builder = Builder(self._name, config)

        # Some global data
        self._version = '2019.07+olimex1'
        self._arch = self._config['arch']
        self._binary = None
        self._package_deb = 'u-boot-sunxi_{}_{}.deb'.format(self._version, self._arch)

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
            return self._config['depends']
        except KeyError:
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
        Downloader(self._name, self._config).download()
        self._builder.extract()

    def configure(self):
        """
        Specify u-boot defconfig

        :return: None
        """
        self._builder.make("{}_defconfig".format(self._config['defconfig']))

    def build(self):
        """
        Build u-boot from sources

        :return: None
        """
        self._builder.make("CROSS_COMPILE={}".format(self._config['toolchain']['prefix']))

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

        # Install target files
        size = 0
        for f in self._config['install']:
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
                os.path.join(package_dir, 'DEBIAN/control')
            ],
            version=self._version,
            arch=self._arch,
            size=int(size // 1024)
        )

        Templater.install(
            [
                os.path.join(package_dir, 'usr/lib/u-boot/kernel.its')
            ],
            arch=self._arch,
            fdt=environment.board.fdt,
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

        rootfs = environment.paths['rootfs']
        image = environment.paths['image']
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

