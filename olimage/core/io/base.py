import abc


class BaseIO(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @abc.abstractmethod
    def info(self, message: str):
        pass
