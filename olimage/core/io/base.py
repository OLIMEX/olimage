import abc


class IBaseIO(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, text):
        pass

    @abc.abstractmethod
    def __enter__(self):
        pass

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abc.abstractmethod
    def info(self, message: str) -> None:
        pass

    @abc.abstractmethod
    def warning(self, message: str) -> None:
        pass

    @abc.abstractmethod
    def error(self, message: str) -> None:
        pass

    @abc.abstractmethod
    def success(self, message: str) -> None:
        pass

