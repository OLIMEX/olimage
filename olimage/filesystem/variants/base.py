import os

import olimage.environment as env

from olimage.core.io import Console
from olimage.core.parsers.packages.variant import Variant
from olimage.core.utils import Utils
from olimage.filesystem.base import FileSystemBase

from olimage.filesystem.stamp import stamp


class VariantBase(FileSystemBase):
    stages = ['configure', 'cleanup', 'export']
    variant = 'base'

    @stamp
    def configure(self):
        self._prepare_build_dir()

        # Extract fresh copy
        with Console("Extracting archive"):
            Utils.archive.extract(self._build_dir.replace('base', 'lite') + '.tar.gz', self._build_dir)

        # Install packages
        with Console("Installing packages"):
            variant: Variant = env.objects['variant']
            Utils.shell.chroot('apt-get install -y {}'.format(' '.join(variant.packages)), self._build_dir)

    @stamp
    def cleanup(self):
        with Console("APT sources"):
            Utils.shell.chroot('apt-get clean')

    @stamp
    def export(self):
        with Console("Creating archive: {}".format(os.path.basename(self._build_dir) + '.tar.gz')):
            Utils.archive.gzip(self._build_dir)
