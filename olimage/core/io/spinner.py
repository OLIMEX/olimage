import functools
import datetime
import sys
import time

import halo
from colorama import Fore, Style
from halo._utils import encode_utf_8_text, get_terminal_columns


class Spinner(halo.Halo):
    """Wrapper for halo module"""

    def __init__(self, text='', color='cyan', text_color=None, spinner=None, animation=None, placement='left',
                 interval=-1, enabled=True, stream=sys.stdout):
        super().__init__(text, color, text_color, spinner, animation, placement, interval, enabled, stream)

        self._start = None

    def __enter__(self):
        self._start = time.time()
        return super().__enter__()

    def frame(self):
        """Builds and returns the frame to be rendered
        Returns
        -------
        self
        """

        if self._start is None:
            return super().frame()

        frames = self._spinner['frames']
        frame = frames[self._frame_index]

        if self._color:
            frame = halo._utils.colored_frame(frame, self._color)

        self._frame_index += 1
        self._frame_index = self._frame_index % len(frames)

        text_frame = self.text_frame()
        delta = int(time.time() - self._start)

        return u'{} {:73} {}{}{}'.format(*[
            (text_frame, frame, '')
            if self._placement == 'right' else
            (frame, text_frame, Fore.YELLOW,  datetime.timedelta(seconds=delta) if delta > 0 else '', Style.RESET_ALL),
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

    def _get_text(self, text):
        """Creates frames based on the selected animation
        Returns
        -------
        self
        """
        animation = self._animation

        # Check which frame of the animation is the widest
        max_spinner_length = max([len(i) for i in self._spinner['frames']])

        # Subtract to the current terminal size the max spinner length
        # (-1 to leave room for the extra space between spinner and text)
        terminal_width = get_terminal_columns() - max_spinner_length - 1
        text_length = len(text)

        frames = []

        if terminal_width < text_length and animation:
            if animation == 'bounce':
                """
                Make the text bounce back and forth
                """
                for x in range(0, text_length - terminal_width + 1):
                    frames.append(text[x:terminal_width + x])
                frames.extend(list(reversed(frames)))
            elif 'marquee':
                """
                Make the text scroll like a marquee
                """
                text = text + ' ' + text[:terminal_width]
                for x in range(0, text_length + 1):
                    frames.append(text[x:terminal_width + x])
        elif terminal_width < text_length and not animation:
            # Add ellipsis if text is larger than terminal width and no animation was specified
            frames = [text[:terminal_width - 6] + ' (...)']
        else:
            frames = [text]

        return {
            'original': text,
            'frames': frames
        }

    def start(self, text=None):
        self._start = time.time()
        return super().start(text=text)

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
        if self._start is None:
            return super().stop_and_persist(symbol=symbol, text=text)

        if not self.enabled:
            return self

        symbol = halo._utils.decode_utf_8_text(symbol)

        if text is not None:
            text = halo._utils.decode_utf_8_text(text)
        else:
            text = self._text['original']

        if self._text_color:
            text = halo._utils.colored_frame(text, self._text_color)

        self.stop()

        delta = int(time.time() - self._start)

        output = u'{} {:73} {}{}{}\n'.format(*[
            (text, symbol, '')
            if self._placement == 'right' else
            (symbol, text, Fore.YELLOW, datetime.timedelta(seconds=delta) if delta > 0 else '', Style.RESET_ALL)
        ][0])

        try:
            self._write(output)
        except UnicodeEncodeError:
            self._write(encode_utf_8_text(output))

        return self
