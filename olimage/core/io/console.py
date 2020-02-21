import olimage.environment as env

from .spinner import SpinnerIO
from .terminal import TerminalIO


class Console(object):
    def __new__(cls, *args, **kwargs):
        if env.options['verbose']:
            _cls = TerminalIO
        else:
            _cls = SpinnerIO

        return _cls(*args, **kwargs)
