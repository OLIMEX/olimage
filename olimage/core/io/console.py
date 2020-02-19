import colorama

from .exceptions import ConsoleException
from .spinner import Spinner

from .base import BaseIO

_depth = 0
_spinner = None


class Console(BaseIO):
    def __init__(self, text=None):
        self._text = text

        global _spinner
        if _spinner and _depth != 0:
            _spinner.succeed()
        _spinner = Spinner()

    def __enter__(self):
        global _depth
        if self._text:
            _spinner.start(self._format(self._text, _depth))

        _depth += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _depth
        _depth -= 1

        global _spinner
        if _spinner:
            if isinstance(exc_type, Exception.__class__):
                _spinner.fail()
            else:
                _spinner.succeed()
            _spinner = None

    @staticmethod
    def _format(message: str, level: int) -> str:
        if 0 > level > 4:
            raise ConsoleException("Console print level must be between 0 and 4")

        indent = '    ' * level + '-'

        if level == 0:
            style = colorama.Style.BRIGHT
        else:
            style = colorama.Style.RESET_ALL

        return "{} {}{}{}".format(indent, style, message, colorama.Style.RESET_ALL)

    @staticmethod
    def _box(message: str, font) -> None:
        message = ' ' * 2 + message + ' ' * 2

        print("{}{}{}".format(font, ' ' * len(message), colorama.Style.RESET_ALL))
        print("{}{}{}".format(font, message, colorama.Style.RESET_ALL))
        print("{}{}{}".format(font, ' ' * len(message), colorama.Style.RESET_ALL))

    @staticmethod
    def info(message: str) -> None:
        print("{}I: {}{}".format(colorama.Style.BRIGHT, message, colorama.Style.RESET_ALL))

    @staticmethod
    def warning(message: str) -> None:
        print("{}W: {}{}".format(colorama.Style.BRIGHT + colorama.Fore.YELLOW, message, colorama.Style.RESET_ALL))

    @staticmethod
    def error(message: str) -> None:
        print("{}E: {}{}".format(colorama.Style.BRIGHT + colorama.Fore.RED, message, colorama.Style.RESET_ALL))

    @staticmethod
    def success(message: str) -> None:
        font = colorama.Back.GREEN + colorama.Fore.WHITE + colorama.Style.BRIGHT
        Console._box(message, font)
