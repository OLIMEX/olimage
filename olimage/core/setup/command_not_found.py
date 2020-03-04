from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupCommandNotFound(SetupAbstract):
    def setup(self):

        # Install
        with Console("Installing packages"):
            Utils.shell.chroot('apt-get install -y {}'.format(' '.join(self.packages)))

        # Configure
        with Console("Updating database"):
            Utils.shell.chroot('update-command-not-found')
