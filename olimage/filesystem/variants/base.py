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

        # Copy resolv.conf
        with Console("Copying /etc/resolv.conf"):
            Utils.shell.run('rm -vf {}/etc/resolv.conf'.format(self._build_dir), ignore_fail=True)
            Utils.shell.run('cp -vf /etc/resolv.conf {}/etc/resolv.conf'.format(self._build_dir))

        # Install packages
        self._install_packages()

        # Configure blueman
        with Console("Configuring blueman"):
            Setup.blueman()

        # Enabling auto-login
        with Console("Enabling auto-login"):
            Utils.install('/etc/lightdm/lightdm.conf')

        # Set default displaymanager
        with Console("Setting default display-manager"):
            Setup.displaymanager("lightdm")

        # post-install
        with Console("Post-install tasks"):
            Utils.shell.chroot("/bin/bash -c 'echo -en > /etc/modules-load.d/cups-filters.conf'", ignore_fail=True)

            # meh broken light-locker in focal
            Utils.shell.chroot('apt-get -y --purge remove light-locker', log_error=False)

    @stamp
    @export(final=True)
    @prepare
    def cleanup(self):
        super().cleanup()

