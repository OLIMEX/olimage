import abc

from .allwinner.sun7i import SUN7I

class BootloaderAbstract(metaclass=abc.ABCMeta):
    @abc.abstractstaticmethod
    def supported():
        pass

    @abc.abstractstaticmethod
    def install():
        pass


class Bootloader(object):
    @staticmethod
    def get():
        return SUN7I