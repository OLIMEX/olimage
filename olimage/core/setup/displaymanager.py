import olimage.environment as env

from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupDisplayManager(SetupAbstract):

    def setup(self, displaymanager: str):
        with Console("Setting default display-manager: \'{}\'".format(displaymanager)):
            Utils.shell.chroot(
                'bash -c \'\
                echo "/usr/sbin/{displaymanager}" > /etc/X11/default-display-manager; \
                \''.format(displaymanager=displaymanager),
                env.paths['build']
            )

            # Reconfigure
            Utils.shell.chroot('dpkg-reconfigure -f noninteractive {}'.format(displaymanager))
