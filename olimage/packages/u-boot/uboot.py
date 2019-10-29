import logging
import os
import shlex
import shutil

from olimage.core.parsers import Partitions
from olimage.core.stamp import stamp
from olimage.core.utils import Utils
from olimage.packages.package import AbstractPackage
from olimage.utils import (Builder, Downloader, Templater, Worker)

import olimage.environment as env

logger = logging.getLogger(__name__)


class Uboot(AbstractPackage):

    def __init__(self, boards, partitions: Partitions):

        self._name = 'u-boot'

        super().__init__(boards)
        self._partitions = partitions


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

    @stamp
    def patch(self):
        """
        Apply patches

        :return: None
        """
        Utils.patch.apply(self._path['patches'], self._path['build'])

    @stamp
    def configure(self):
        """
        Specify u-boot defconfig

        1. Apply defconfig
        2. Modify CONFIG_ENV_EXT4_DEVICE_AND_PART

        :return: None
        """
        self._builder.make("{}_defconfig".format(self._package.defconfig))

        # Configure uboot.env location, depending on partition table
        device = '0:auto'
        file = '/boot/uboot.env'

        for i in range(len(self._partitions)):
            if self._partitions[i].fstab.mount == '/boot':
                device = '0:{}'.format(i)
                file = 'uboot.env'
                break

        with open(os.path.join(self._builder.paths['extract'], '.config'), 'r') as f:
            lines = f.readlines()
        with open(os.path.join(self._builder.paths['extract'], '.config'), 'w') as f:
            for line in lines:
                if 'CONFIG_ENV_EXT4_DEVICE_AND_PART' in line:
                    line = 'CONFIG_ENV_EXT4_DEVICE_AND_PART="{}"\n'.format(device)
                elif 'CONFIG_ENV_EXT4_FILE' in line:
                    line = 'CONFIG_ENV_EXT4_FILE="{}"\n'.format(file)
                f.write(line)

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

        # The FIT image is always located in /boot directory.
        # If there is such defined partition retrieve it's number. Do the same for /
        partitions = {
            'boot': 1,
            'root': 1
        }
        for i in range(len(self._partitions)):
            partition  = self._partitions[i]
            if partition.fstab.mount == '/':
                partitions['root'] = i + 1
            elif partition.fstab.mount == '/boot':
                partitions['boot'] = i + 1

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
            partitions=partitions,
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

        # Generate fdts and overlay data
        fdts = []
        overlays = []
        for variant in self._board.variants:
            if variant.fdt not in fdts:
                fdts.append(variant.fdt)

            for overlay in variant.overlays:
                if overlay not in overlays:
                    overlays.append(overlay)

        # Remap board fdt and overlays
        variants = []
        for variant in self._board.variants:

            dtbo = []
            for overlay in variant.overlays:
                dtbo.append(overlays.index(overlay) + 1)

            variants.append({
                'name': str(variant),
                'fdt': fdts.index(variant.fdt) + 1,
                'id': variant.id,
                'overlays': dtbo,
                'compatible': 'olimex,{}'.format(str(variant).lower())
            })

        # Generate load addresses for fdt files
        temp = []
        for fdt in fdts:
            temp.append({fdt: {'load': '0x4FA00000'}})
        fdts = temp

        # Generate load addresses for overlays
        addr = 0x4FA10000
        temp = []
        for overlay in overlays:
            temp.append({overlay: {'load': '0x{:08X}'.format(addr)}})
            addr += 0x10000
        overlays = temp

        Templater.install(
            [
                os.path.join(package_dir, 'usr/lib/u-boot/kernel.its')
            ],
            arch=self._arch,
            default=self._board.default,
            fdts=fdts,
            kernel={
                'load': '0x40080000',
                'entry': '0x40080000'
            },
            overlays=overlays,
            ramdisk={
                'load': '0x4FE00000',
                'entry': '0x4FE00000'
            },
            variants=variants,
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
