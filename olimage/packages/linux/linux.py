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
import shlex
import os

from olimage.packages import Package
from olimage.utils.downloader import Downloader
from olimage.utils.builder import Builder
from olimage.utils.worker import Worker

import olimage.environment as environment

logger = logging.getLogger(__name__)


class Linux(Package):

    def __init__(self, config):

        self._name = 'linux'
        self._config = config

        self._builder = Builder(self._name, self._config)

        # Initialize callback methods
        callbacks = {
            'download':     self._download,
            'configure':    self._configure,
            'build':        self._build,
            'package':      self._package,
            'install':      self._install,
        }
        super().__init__(**callbacks)

        # Some global data
        self._arch = self._config['arch']
        self._toolchain = self._config['toolchain']['prefix']

        self._version = None

    @staticmethod
    def alias():
        return 'linux'

    @property
    def dependency(self):
        try:
            return self._config['depends']
        except KeyError:
            return []

    def __str__(self):
        return self._name

    def _download(self):
        """
        Download sources. Currently only git is supported

        :return: None
        """
        Downloader(self._name, self._config).download()
        self._builder.extract()

    def _configure(self):
        """
        Configure sources using defconfig

        :return: None
        """

        defconfig = 'defconfig'

        if self._config['defconfig'] is not None:
            defconfig = self._config['defconfig'] + '_defconfig'

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

    def _build(self):
        self._builder.make("ARCH={} CROSS_COMPILE={} {}".format(self._arch,self._toolchain,' '.join(self._config['targets'])))

    def _package(self):
        """
        Package linux kernel

        :return: None
        """
        self._version = self._builder.make("kernelversion").decode().splitlines()[1]
        self._builder.make("KDEB_PKGVERSION={}-1-olimex LOCALVERSION=-1-olimex ARCH={} CROSS_COMPILE={} bindeb-pkg".format(self._version, self._arch, self._toolchain))

    def _install(self):
        """
        Install u-boot into the target rootfs

        1. Copy .deb file
        2. Run chroot and install
        3. Remove .deb file
        4. Flash binary

        :return: None
        """
        #
        rootfs = environment.paths['rootfs']
        build = self._builder.paths['build']

        # Copy file
        Worker.run(shlex.split('cp -vf {} {}'.format(os.path.join(build, 'linux-image-5.3.1-1-olimex_5.3.1-1-olimex_arm64.deb'), rootfs)), logger)

        # Install
        Worker.chroot(shlex.split('dpkg -i {}'.format(os.path.basename('linux-image-5.3.1-1-olimex_5.3.1-1-olimex_arm64.deb'))), rootfs, logger)

        # Remove file
        Worker.run(shlex.split('rm -vf {}'.format(os.path.join(rootfs, 'linux-image-5.3.1-1-olimex_5.3.1-1-olimex_arm64.deb'))), logger)

