import olimage.environment as env

from olimage.core.io import Console
from olimage.core.parsers.packages.variant import Variant
from olimage.core.setup import Setup
from olimage.core.utils import Utils
from olimage.filesystem.filesystem import FileSystemBase

from olimage.filesystem.stamp import stamp


class FileSystemBase(FileSystemBase):
    variant = 'base'

    def configure(self):
        self._prepare_build_dir()

        Utils.archive.extract(self._build_dir.replace('base', 'lite') + '.tar.gz', self._build_dir)

        with Console("Configuring locales"):
            Setup.locales(env.options['locale'])

        # Install packages
        with Console("Installing packages"):
            variant: Variant = env.objects['variant']
            Utils.shell.chroot('apt-get install -y {}'.format(' '.join(variant.packages)), self._build_dir)
