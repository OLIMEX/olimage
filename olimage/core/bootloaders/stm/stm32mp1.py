import os
import re
import olimage.environment as env

from olimage.core.bootloaders.base import BootloaderAbstract
from olimage.core.utils import Utils
from olimage.core.io import Console


class BootloaderSTM32MP1(BootloaderAbstract):
    @staticmethod
    def compatible() -> str:
        """
        Return supported devices. Must match SoC type defined in the boards definitions

        :return: Supported SoC.
        """
        return 'stm32mp1xx'

    def install(self, output: str):
        board = env.objects['board']

        # map
        lines = Utils.shell.run('kpartx -avs {}'.format(output)).decode('utf-8', 'ignore')
        for line in lines.splitlines():
            w = line.split()
            if w[0] == 'add':
                index = int(re.match(r'^loop(\d+)p(\d+)$', w[2])[1])
                device = '/dev/mapper/loop' + str(index)

        with Console("Writing \'u-boot-spl.stm32\'"):
            # u-boot-spl.stm32 on part1 and part2
            src = "/usr/lib/u-boot-olinuxino/{}/u-boot-spl.stm32".format(board.name.lower())
            Utils.shell.run(
                'dd if={} of={} conv=sync,fsync,notrunc'.format(
                    env.paths['build'] + src,
                    device + "p1"
                ))
            Utils.shell.run(
                'dd if={} of={} conv=sync,fsync,notrunc'.format(
                    env.paths['build'] + src,
                    device + "p2"
                ))
        with Console("Writing \'u-boot.img\'"):
            # u-boot.img on part3
            src = "/usr/lib/u-boot-olinuxino/{}/u-boot.img".format(board.name.lower())
            Utils.shell.run(
                'dd if={} of={} conv=sync,fsync,notrunc'.format(
                    env.paths['build'] + src,
                    device + "p3"
                ))

        # unmap
        Utils.shell.run('kpartx -dvs {}'.format(output))
