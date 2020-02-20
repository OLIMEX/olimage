import olimage.environment as env

from olimage.core.io import Console
from olimage.core.parsers.packages.variant import Variant
from olimage.core.utils import Utils
from olimage.filesystem.base import FileSystemBase

from olimage.filesystem.stamp import stamp


class FileSystemLite(FileSystemBase):
    stages = ['configure']
    variant = 'lite'

    def configure(self):
        self._prepare_build_dir()

        # Extract fresh copy
        with Console("Extracting archive"):
            Utils.archive.extract(self._build_dir.replace('lite', 'minimal') + '.tar.gz', self._build_dir)

        # Install packages
        with Console("Installing packages"):
            variant: Variant = env.objects['variant']
            Utils.shell.chroot('apt-get install -y {}'.format(' '.join(variant.packages)), self._build_dir)
