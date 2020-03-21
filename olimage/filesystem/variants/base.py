from olimage.core.io import Console
from olimage.core.setup import Setup
from olimage.core.utils import Utils

from olimage.filesystem.decorators import export, prepare, stamp
from olimage.filesystem.base import FileSystemBase


class VariantBase(FileSystemBase):
    stages = ['configure', 'cleanup']
    variant = 'base'

    @stamp
    @export
    @prepare
    def configure(self):

        # Install packages
        self._install_packages()

        # Configure blueman
        with Console("Configuring blueman"):
            Setup.blueman()

    @stamp
    @export(final=True)
    @prepare
    def cleanup(self):
        super().cleanup()

