from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import ServiceBase


class ServiceSSH(ServiceBase):
    @staticmethod
    def enable():
        with Console('Enabling: \'ssh\''):
            Utils.shell.chroot('systemctl enable ssh')

    @staticmethod
    def disable():
        with Console('Disabling: \'ssh\''):
            Utils.shell.chroot('systemctl disable ssh')

