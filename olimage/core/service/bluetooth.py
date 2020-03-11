import olimage.environment as env

from olimage.core.io import Console
from olimage.core.utils import Utils
from olimage.core.parsers import Board

from .base import ServiceBase


class ServiceBluetooth(ServiceBase):
    @staticmethod
    def enable() -> None:
        board: Board = env.objects['board']
        with Console('Enabling: \'olinuxino-bluetooth.service\''):
            source = env.paths['overlay'] + '/usr/sbin/rtk_hciattach.{}'.format(board.arch)
            dest = env.paths['build'] + '/usr/sbin/rtk_hciattach'

            Utils.shell.run('install -D -v -m 755 {} {}'.format(source, dest))

            Utils.install(
                [
                    '/usr/lib/olinuxino/olinuxino-bluetooth',
                    '/etc/systemd/system/olinuxino-bluetooth.service'
                ],
                mode='755')

            Utils.shell.chroot("systemctl enable olinuxino-bluetooth.service")


    @staticmethod
    def disable() -> None:
        with Console('Disabling: \'olinuxino-bluetooth.service\''):
            Utils.shell.chroot("systemctl disable olinuxino-bluetooth.service")
