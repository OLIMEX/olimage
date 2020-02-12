import abc


class BootloaderAbstract(metaclass=abc.ABCMeta):
    @abc.abstractstaticmethod
    def supported():
        pass

    @abc.abstractstaticmethod
    def install(board, output):
        pass
