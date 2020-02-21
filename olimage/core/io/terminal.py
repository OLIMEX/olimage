import sys

from colorama import Back, Fore, Style

from .base import IBaseIO


class TerminalIO(IBaseIO):
    def __init__(self, text=None):
        self._text = text

    def __enter__(self):
        if self._text:
            self.info(self._text)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    def _print(message: str) -> None:
        print(message)

    @staticmethod
    def info(message: str) -> None:
        TerminalIO._print("{}I: {}{}".format(Style.BRIGHT, message, Style.RESET_ALL))

    @staticmethod
    def warning(message: str) -> None:
        TerminalIO._print("{}W: {}{}".format(Style.BRIGHT + Fore.YELLOW, message, Style.RESET_ALL))

    @staticmethod
    def error(message: str) -> None:
        TerminalIO._print("{}E: {}{}".format(Style.BRIGHT + Fore.RED, message, Style.RESET_ALL))

    @staticmethod
    def success(message: str) -> None:
        TerminalIO._print("{}{}{}".format(Style.BRIGHT + Fore.GREEN, message, Style.RESET_ALL))




