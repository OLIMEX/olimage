import logging
import os
import shlex
import shutil

from olimage.utils.builder import Builder
from olimage.utils.downloader import Downloader
from olimage.utils.printer import Printer
from olimage.utils.templater import Templater
from olimage.utils.worker import Worker
from olimage.packages import Package

import olimage.environment as environment


logger = logging.getLogger(__name__)


class Uboot(Package):

    def __init__(self, config):

        self._name = 'u-boot'
        self._config = config

        # Configure builder
        self._builder = Builder(self._name, config)

    @staticmethod
    def alias():
        return 'u-boot'

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
        self._builder.extract()
        self._builder.configure("{}_defconfig".format(self._config['defconfig']))
        self._builder.build("CROSS_COMPILE={}".format(self._config['toolchain']['prefix']))

        return self

    def package(self):
        """
        Generate debian package from sources

        :return: self
        """
        pkg_dir = os.path.join(self._builder.paths['build'], 'u-boot-sunxi')
        logger.info("Preparing build directory: {}".format(pkg_dir))

        if os.path.exists(pkg_dir):
            shutil.rmtree(pkg_dir)
        os.mkdir(pkg_dir)

        # Install target files
        size = 0
        for f in self._config['install']:
            src, dest = f.split(':')

            dest = os.path.join(pkg_dir, dest)

            if not os.path.exists(dest):
                os.makedirs(dest)

            logger.info("Copying {} to {}".format(src, dest))
            dest = os.path.join(dest, src)
            src = os.path.join(self._builder.paths['extract'], src)

            shutil.copyfile(src, dest)
            size += os.path.getsize(dest)

        # Copy overlay
        Worker.run(
            ["cp -rvf {}/overlay/* {}".format(os.path.dirname(os.path.abspath(__file__)), pkg_dir)],
            logger,
            shell=True)

        # Generate template files
        version = '2019.07+olimex1'
        arch = self._config['arch']
        deb = os.path.join(self._builder.paths['build'], 'u-boot-sunxi_{}_{}.deb'.format(version, arch))

        Templater.install(
            [
                os.path.join(pkg_dir, 'DEBIAN/control')
            ],
            version=version,
            arch=arch,
            size=int(size // 1024),
            platforms=['a64-olinuxino']
        )

        # Build package
        Worker.run(shlex.split('dpkg-deb -b {} {}'.format(pkg_dir, deb)), logger)

        return self
