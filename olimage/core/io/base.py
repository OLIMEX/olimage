import abc


class BaseIO(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def info(self, message: str):
        pass
