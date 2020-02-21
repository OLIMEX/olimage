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

    @staticmethod
    @abc.abstractmethod
    def info(message: str) -> None:
        pass

    @staticmethod
    @abc.abstractmethod
    def warning(message: str) -> None:
        pass

    @staticmethod
    @abc.abstractmethod
    def error(message: str) -> None:
        pass

    @staticmethod
    @abc.abstractmethod
    def success(message: str) -> None:
        pass

