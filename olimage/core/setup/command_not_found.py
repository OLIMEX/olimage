import olimage.environment as env

from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupCommandNotFound(SetupAbstract):
    def setup(self):

        # Install
        with Console("Installing packages"):
            Utils.shell.chroot('apt-get install -y {}'.format(' '.join(self.packages)))

        """
        On debian there is no command-not-found-data package. Thus the database
        must be updated.
        
        Note: This must be run before apt-get clean
        """
        if str(env.objects['distribution']) == 'debian':
            with Console("Updating database"):
                Utils.shell.chroot('update-command-not-found')
