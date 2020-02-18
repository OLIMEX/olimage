import abc


class BootloaderAbstract(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def compatible() -> str:
        pass

    @abc.abstractmethod
    def install(self, output: str) -> None:
        pass
