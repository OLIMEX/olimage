from olimage.core.io import Console
from olimage.core.setup import Setup
from olimage.core.utils import Utils

from olimage.filesystem.base import FileSystemBase
from olimage.filesystem.decorators import export, prepare, stamp


class VariantLite(FileSystemBase):
    stages = ['configure', 'cleanup']
    variant = 'lite'

    @stamp
    @export
    @prepare
    def configure(self):

        # Copy resolv.conf
        with Console("Copying /etc/resolv.conf"):
            Utils.shell.run('rm -vf {}/etc/resolv.conf'.format(self._build_dir), ignore_fail=True)
            Utils.shell.run('cp -vf /etc/resolv.conf {}/etc/resolv.conf'.format(self._build_dir))

        # Install packages
        self._install_packages()

        # Update command-not-found database
        with Console("Configuring command-not-found:"):
            Setup.command_not_found()

    @stamp
    @export(final=True)
    @prepare
    def cleanup(self):
        super().cleanup()
