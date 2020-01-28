from olimage.core.bootloaders.bootloader import BootloaderAbstract


class SUN7I(BootloaderAbstract):
    @staticmethod
    def supported():
        """
        Return supported devices

        :return: list with supported devices
        """
        return [
            'sun7i_a20'
        ]

    @staticmethod
    def install():
        pass
