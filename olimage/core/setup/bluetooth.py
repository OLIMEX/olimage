import olimage.environment as env

from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupBluetooth(SetupAbstract):
    def setup(self):

        with Console("Installing packages"):
            # This will fail due blueman not detecting chroot environment.
            # Ignore the error and do some dpkg magic
            try:
                Utils.shell.chroot('apt-get install -y {}'.format(' '.join(self.packages)), log_error=False)
                return
            except Exception:
                pass

            Utils.shell.run('sed -i "/^set -e/d" {}/var/lib/dpkg/info/blueman.postinst'.format(env.paths['build']))
            Utils.shell.chroot('apt-get install -y -f')

