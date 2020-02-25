from olimage.core.io import Console
from olimage.core.setup import Setup
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
        self._install_packages()

        # Configure bluetooth
        with Console("Configuring bluetooth"):
            Setup.bluetooth()

    @stamp
    def cleanup(self):
        super().cleanup()

    @stamp
    def export(self):
        super().export()
