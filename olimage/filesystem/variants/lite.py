import os

import olimage.environment as env

from olimage.core.io import Console
from olimage.core.parsers.packages.variant import Variant
from olimage.core.utils import Utils
from olimage.filesystem.base import FileSystemBase

from olimage.filesystem.stamp import stamp


class VariantLite(FileSystemBase):
    stages = ['configure', 'cleanup', 'export']
    variant = 'lite'

    @stamp
    def configure(self):
        self._prepare_build_dir()

        # Extract fresh copy
        with Console("Extracting archive"):
            Utils.archive.extract(self._build_dir.replace('lite', 'minimal') + '.tar.gz', self._build_dir)

        # Copy resolv.conf
        with Console("Copying /etc/resolv.conf"):
            Utils.shell.run('rm -vf {}/etc/resolv.conf'.format(self._build_dir), ignore_fail=True)
            Utils.shell.run('cp -vf /etc/resolv.conf {}/etc/resolv.conf'.format(self._build_dir))

        # Install packages
        self._install_packages()

    @stamp
    def cleanup(self):
        super().cleanup()

    @stamp
    def export(self):
        super().export()
