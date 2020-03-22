import olimage.environment as env

from olimage.core.bootloaders.base import BootloaderAbstract
from olimage.core.utils import Utils
from olimage.core.io import Console


class BootloaderA10(BootloaderAbstract):
    @staticmethod
    def compatible() -> str:
        """
        Return supported devices. Must match SoC type defined in the boards definitions

        :return: Supported SoC.
        """
        return 'sun4i-a10'

    def install(self, output: str):
        with Console("Writing \'u-boot-sunxi-with-spl.bin\'"):
            Utils.shell.run(
                'dd if={} of={} bs=1k seek=8 conv=sync,fsync,notrunc'.format(
                    env.paths['build'] + "/usr/lib/u-boot-olinuxino/a10-olinuxino/u-boot-sunxi-with-spl.bin",
                    output
                ))
