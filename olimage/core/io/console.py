import olimage.environment as env

from .spinner import SpinnerIO
from .terminal import TerminalIO


class ConsoleMeta(type):
    def __getattribute__(self, item):
        if 'verbose' in env.options:
            if env.options['verbose']:
                _cls = TerminalIO
            else:
                _cls = SpinnerIO

            if item in _cls.__dict__:
                _func = _cls.__dict__[item]
                return _func.__func__

        return super().__getattribute__(item)


class Console(object, metaclass=ConsoleMeta):
    def __new__(cls, *args, **kwargs):
        if env.options['verbose']:
            _cls = TerminalIO
        else:
            _cls = SpinnerIO

        return _cls(*args, **kwargs)
