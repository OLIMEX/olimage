# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Olimex Ltd.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import os
import shlex
import shutil

from olimage.utils.builder import Builder
from olimage.utils.downloader import Downloader
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

        # Initialize callback methods
        callbacks = {
            'download':     self._download,
            'configure':    self._configure,
            'build':        self._build,
            'package':      self._package,
            'install':      self._install
        }
        super().__init__(**callbacks)

        # Some global data
        self._version = '2019.07+olimex1'
        self._arch = self._config['arch']
        self._package_deb = os.path.join(
            self._builder.paths['build'],
            'u-boot-sunxi_{}_{}.deb'.format(self._version, self._arch))

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

    def _download(self):
        """
        Download u-boot sources

        1. Clone repository
        2. Create archive
        3. Extract archive to the build directory

        :return:
        """
        Downloader(self._name, self._config).download()
        self._builder.extract()

    def _configure(self):
        """
        Specify u-boot defconfig

        :return: None
        """
        self._builder.make("{}_defconfig".format(self._config['defconfig']))

    def _build(self):
        """
        Build u-boot from sources

        :return: None
        """
        self._builder.make("CROSS_COMPILE={}".format(self._config['toolchain']['prefix']))

    def _package(self):
        """
        Generate .deb file

        1. Create directory structure
        2. Copy install files
        3. Install control files
        4. Generate .deb file

        :return: None
        """
        package_dir = os.path.join(self._builder.paths['build'], 'u-boot-sunxi')
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

        # Build package
        Worker.run(shlex.split('dpkg-deb -b {} {}'.format(package_dir, self._package_deb)), logger)

    def _install(self):
        """
        Install u-boot into the target rootfs

        1. Copy .deb file
        2. Run chroot and install
        3. Remove .deb file

        :return: None
        """
        rootfs = environment.paths['rootfs']

        # Copy file
        Worker.run(shlex.split('cp -vf {} {}'.format(self._package_deb, rootfs)), logger)

        # Install
        Worker.chroot(shlex.split('dpkg -i {}'.format(os.path.basename(self._package_deb))), rootfs, logger)

        # Remove file
        Worker.run(shlex.split('rm -vf {}'.format(self._package_deb)), logger)

