from olimage.core.printer import Printer

_previous_printer = None


class OutputBase(object):
    def __init__(self, text):

        if self.level == 1:
            text = '-> ' + text
        elif self.level == 2:
            text = '---> ' + text
        else:
            raise Exception("Unknown output level: \'{}\'".format(self.level))

        global _previous_printer
        if _previous_printer:
            _previous_printer.succeed()

        self._printer = Printer(text)
        _previous_printer = self._printer

    def print(self):
        global _previous_printer
        _previous_printer = None
        return self._printer.start().succeed()

    def __enter__(self):
        self._printer.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _previous_printer
        if _previous_printer is None:
            return

        _previous_printer = None

        if isinstance(exc_type, Exception.__class__):
            self._printer.fail()
        else:
            self._printer.succeed()


class _Step(OutputBase):
    level = 1


class _Substep(OutputBase):
    level = 2


class Output(object):
    step = _Step
    substep = _Substep