from olimage.core.utils import Utils

from .base import ServiceBase


class Getty(ServiceBase):
    @staticmethod
    def name() -> str:
        return 'getty@tty1.service.d/noclear.conf'

    @staticmethod
    def install() -> None:
        Utils.install('/etc/systemd/system/getty@tty1.service.d/noclear.conf')

    @staticmethod
    def uninstall() -> None:
        Utils.shell.chroot('rm -vf /etc/systemd/system/getty@tty1.service.d/noclear.conf')
