from olimage.core.io import Console
from olimage.core.utils import Utils

from .base import ServiceBase


class ServiceFirstBoot(ServiceBase):
    @staticmethod
    def enable() -> None:
        with Console('Enabling: \'olinuxino-firstboot.service\''):
            Utils.install(
                [
                    '/usr/lib/olinuxino/olinuxino-firstboot',
                    '/etc/systemd/system/olinuxino-firstboot.service'
                ],
                mode='755')

            Utils.shell.chroot("systemctl enable olinuxino-firstboot.service")

    @staticmethod
    def disable() -> None:
        with Console('Disabling: \'olinuxino-firstboot.service\''):
            Utils.shell.chroot("systemctl disable olinuxino-firstboot.service")
