import olimage.environment as env

from olimage.core.bootloaders.base import BootloaderAbstract
from olimage.core.utils import Utils
from olimage.core.parsers import (Board)


class Sun7iA20(BootloaderAbstract):
    @staticmethod
    def supported():
        """
        Return supported devices

        :return: list with supported devices
        """
        return [
            'sun7i-a20'
        ]

    @staticmethod
    def install(board: Board, output: str):
        Utils.shell.run(
            'dd if={} of={} bs=1k seek=8 conv=sync,fsync,notrunc'.format(
                env.paths['debootstrap'] + "/usr/lib/u-boot-olinuxino/a20-olinuxino/u-boot-sunxi-with-spl.bin",
                output
            ))
