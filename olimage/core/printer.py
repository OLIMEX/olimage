import functools
import datetime
import sys
import time

import halo
from halo._utils import encode_utf_8_text


class Printer(halo.Halo):
    """Wrapper for halo module"""

    def __init__(self, text='', color='cyan', text_color=None, spinner=None, animation=None, placement='left',
                 interval=-1, enabled=True, stream=sys.stdout):
        super().__init__(text, color, text_color, spinner, animation, placement, interval, enabled, stream)

        self._start = None

    def __enter__(self):
        self._start = time.time()
        return super().__enter__()

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)

    def frame(self):
        """Builds and returns the frame to be rendered
        Returns
        -------
        self
        """
        frames = self._spinner['frames']
        frame = frames[self._frame_index]

        if self._color:
            frame = halo._utils.colored_frame(frame, self._color)

        self._frame_index += 1
        self._frame_index = self._frame_index % len(frames)

        text_frame = self.text_frame()
        delta = datetime.timedelta(seconds=int(time.time() - self._start))

        return u'{} {:32} {}'.format(*[
            (text_frame, frame, '')
            if self._placement == 'right' else
            (frame, text_frame, delta),
        ][0])

    def __call__(self, f):
        """Allow the Halo object to be used as a regular function decorator."""

        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            with self:
                try:
                    ret = f(*args, **kwargs)
                    self.succeed()
                    return ret

                except Exception as e:
                    self.fail()
                    raise e

        return wrapped

    def stop_and_persist(self, symbol=' ', text=None):
        """Stops the spinner and persists the final frame to be shown.
        Parameters
        ----------
        symbol : str, optional
            Symbol to be shown in final frame
        text: str, optional
            Text to be shown in final frame

        Returns
        -------
        self
        """
        if not self.enabled:
            return self

        symbol = halo._utils.decode_utf_8_text(symbol)

        if text is not None:
            text = halo._utils.decode_utf_8_text(text)
        else:
            text = self._text['original']

        text = text.strip()

        if self._text_color:
            text = halo._utils.colored_frame(text, self._text_color)

        self.stop()

        delta = datetime.timedelta(seconds=int(time.time() - self._start))

        output = u'{} {:32} {}\n'.format(*[
            (text, symbol, '')
            if self._placement == 'right' else
            (symbol, text, delta)
        ][0])

        try:
            self._write(output)
        except UnicodeEncodeError:
            self._write(encode_utf_8_text(output))

        return self


class PrinterProcess(Printer):
    def __init__(self, text='', color='cyan', text_color=None, spinner=None, animation=None, placement='left',
                 interval=-1, enabled=True, stream=sys.stdout):
        super().__init__('... ' + text, color, text_color, spinner, animation, placement, interval, enabled, stream)


class PrinterHeader(object):
    def __init__(self, text=''):
        self._text = text

    def __call__(self, f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            print('\n' + self._text)
            return f(*args, **kwargs)
        return wrapped


class Print():
    header = PrinterHeader
    process = PrinterProcess
