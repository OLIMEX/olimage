from olimage.core.utils import Utils

from .base import ServiceBase


class Resize(ServiceBase):

    @staticmethod
    def name() -> str:
        return 'olinuxino-expand.service'

    @staticmethod
    def enable() -> None:
        Utils.install(
            [
                '/usr/lib/olinuxino/olinuxino-expand',
                '/etc/systemd/system/olinuxino-expand.service'
            ],
            mode='755')

        # Enable service
        Utils.shell.chroot("systemctl enable olinuxino-expand.service")

    @staticmethod
    def disable() -> None:
        Utils.shell.chroot("systemctl disable olinuxino-expand.service")