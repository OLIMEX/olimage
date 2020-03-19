import olimage.environment as env

from olimage.core.io import Console
from olimage.core.utils import Utils
from olimage.core.parsers import Board

from .base import ServiceBase


class ServiceBluetooth(ServiceBase):
    @staticmethod
    def enable() -> None:
        board: Board = env.objects['board']
        with Console('Installing bluetooth firmware'):
            source = env.paths['overlay'] + '/usr/sbin/rtk_hciattach.{}'.format(board.arch)
            dest = env.paths['build'] + '/usr/sbin/rtk_hciattach'

            Utils.shell.run('install -D -v -m 755 {} {}'.format(source, dest))

            Utils.install(
                [
                    '/usr/lib/firmware/rtl_bt/rtl8723b_config.bin',
                    '/usr/lib/firmware/rtl_bt/rtl8723b_fw.bin'
                ]
            )

    @staticmethod
    def disable() -> None:
        pass
