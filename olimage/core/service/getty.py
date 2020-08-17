from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import ServiceBase


class ServiceGetty(ServiceBase):
    @staticmethod
    def enable() -> None:
        with Console('Installing: \'getty@tty1.service.d/noclear.conf\''):
            Utils.install('/etc/systemd/system/getty@tty1.service.d/noclear.conf')

        with Console('Enabling: \'serial-getty@ttyGS0.service\''):
            # Install and enable service
            Utils.shell.chroot('mkdir -p /etc/systemd/system/serial-getty@ttyGS0.service.d')
            Utils.shell.chroot('systemctl --no-reload enable serial-getty@ttyGS0.service')

    @staticmethod
    def disable() -> None:
        with Console('Removing: \'getty@tty1.service.d/noclear.conf\''):
            Utils.shell.chroot('rm -vf /etc/systemd/system/getty@tty1.service.d/noclear.conf')

        with Console('Disabling: \'serial-getty@ttyGS0.service\''):
            Utils.shell.chroot('systemctl disable serial-getty@ttyGS0.service')
