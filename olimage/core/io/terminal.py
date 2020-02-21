from colorama import Fore, Style

from .base import IBaseIO


class TerminalIO(IBaseIO):
    def __init__(self, text=None):
        self._text = text

    def __enter__(self):
        if self._text:
            self.info(self._text)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def info(self, message: str) -> None:
        print("{}I: {}{}".format(Style.BRIGHT, message, Style.RESET_ALL))

    def warning(self, message: str) -> None:
        print("{}W: {}{}".format(Style.BRIGHT + Fore.YELLOW, message, Style.RESET_ALL))

    def error(self, message: str) -> None:
        print("{}E: {}{}".format(Style.BRIGHT + Fore.RED, message, Style.RESET_ALL))

    def success(self, message: str) -> None:
        print("{}{}{}".format(Style.BRIGHT + Fore.GREEN, message, Style.RESET_ALL))




