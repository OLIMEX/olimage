from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import ServiceBase


class ServiceExpand(ServiceBase):
    @staticmethod
    def enable() -> None:
        with Console('Enabling: \'olinuxino-expand.service\''):
            Utils.install(
                [
                    '/usr/lib/olinuxino/olinuxino-expand',
                    '/etc/systemd/system/olinuxino-expand.service'
                ],
                mode='755')

            Utils.shell.chroot("systemctl enable olinuxino-expand.service")

    @staticmethod
    def disable() -> None:
        with Console('Disabling: \'olinuxino-expand.service\''):
            Utils.shell.chroot("systemctl disable olinuxino-expand.service")
