import inspect
import sys

from olimage.core.parsers import (Board)

from .allwinner import *
from .stm import *
from .base import BootloaderAbstract
from .exceptions import BootloaderException


class Bootloader(object):
    def __init__(self, board: Board):

        # Populate available bootloaders
        bootloaders = []
        for _, obj in inspect.getmembers(sys.modules[__name__]):
            if inspect.isclass(obj) and obj != BootloaderAbstract:
                for t in inspect.getmro(obj):
                    if t == BootloaderAbstract:
                        bootloaders.append(obj)
                        break

        # Get bootloader
        self._bootloader = None
        for bootloader in bootloaders:
            if board.soc == bootloader.compatible():
                self._bootloader = bootloader()
                break

        if not self._bootloader:
            raise BootloaderException("There is no matching bootloader for the SoC \'{}\'!".format(board.soc))

    def install(self, output):
        self._bootloader.install(output)

