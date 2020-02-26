import olimage.environment as env

from olimage.core.bootloaders.base import BootloaderAbstract
from olimage.core.utils import Utils
from olimage.core.io import Console


class BootloaderA64(BootloaderAbstract):
    @staticmethod
    def compatible() -> str:
        """
        Return supported devices. Must match SoC type defined in the boards definitions

        :return: Supported SoC.
        """
        return 'sun50i-a64'

    def install(self, output: str):

        source = env.paths['build'] + '/usr/lib/u-boot-olinuxino/a64-olinuxino'

        # Write SPL image
        with Console("Writing \'sunxi-spl.bin\'"):
            Utils.shell.run(
                'dd if={}/sunxi-spl.bin of={} bs=1k seek=8 conv=sync,fsync,notrunc'.format(source, output))

        # Generate U-Boot FIT image
        with Console("Generating \'u-boot.itb\'"):
            temp = Utils.shell.run('mktemp -d').decode().strip()
            Utils.shell.run(
                'cp -vf {build}/usr/lib/arm-trusted-firmware-olinuxino/sun50i_a64/bl31.bin '
                '{source}/sun50i-a64-olinuxino.dtb '
                '{source}/u-boot-nodtb.bin '
                '{source}/u-boot.bin '
                '{build}/usr/bin/mksunxi_fit_atf '
                '{temp}/'.format(build=env.paths['build'], source=source, temp=temp))
            Utils.shell.run(
                'cd {} && '
                'bash mksunxi_fit_atf *.dtb > u-boot.its && '
                'mkimage -f u-boot.its u-boot.itb'.format(temp), shell=True)

        with Console("Writing \'u-boot.itb\'"):
            Utils.shell.run('dd if={}/u-boot.itb of={} conv=notrunc,fsync bs=1k seek=40'.format(temp, output))
            Utils.shell.run('rm -rvf {}'.format(temp))
