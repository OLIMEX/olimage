import logging
import os
import shlex
import shutil
import tarfile

from utils.printer import Printer
from utils.stamper import Stamper
from utils.package import Package
from utils.worker import Worker

logger = logging.getLogger(__name__)


class Builder(Package):

    def __init__(self, name, path, config):
        super().__init__(name, path, config)

        # Configure stamper
        self.stamper = Stamper(self._path['build'])

    @property
    def printer(self):
        return self._printer

    @printer.setter
    def printer(self, printer):
        self._printer = printer

    @Printer("Extracting archive")
    def extract(self):

        self.printer.text += " \'{}\'".format(os.path.basename(self._path['archive']))

        if 'extracted' in self.stamper.get_stamps():
            return self

        # Cleanup directory
        if os.path.exists(self._path['extract']):
            logger.debug("Removing dirty directory: {}".format(self._path['extract']))
            shutil.rmtree(self._path['extract'])

        # Extract sources
        with tarfile.open(name=self._path['archive'], mode='r:gz') as tar:
            tar.extractall(path=self._path['extract'])

        self.stamper.stamp('extracted')

        return self

    @Printer("Configuring package")
    def configure(self, command=None):

        self.printer.text += " \'{}\'".format(self)

        if 'configured' in self.stamper.get_stamps():
            return self

        # Command is none, then assume user whats to skip this step
        if command is None:
            self.stamper.stamp('configured')
            return self

        def handle_output(data):
            for line in data.decode().rstrip().split('\n'):
                logger.debug(line)

        Worker.run(
            shlex.split("/bin/bash -c 'make -C {} {} -j{}'".format(
                self._path['extract'],
                command,
                1 if os.cpu_count() is None else os.cpu_count())
            ),
            stdout_callback=handle_output,
            stderr_callback=handle_output
        )

        return self

    @Printer("Building package")
    def build(self, command):

        self.printer.text += " \'{}\'".format(self)

        # Command is none, then assume user whats to skip this step
        if command is None:
            return self

        def handle_output(data):
            for line in data.decode().rstrip().split('\n'):
                logger.debug(line)

        Worker.run(
            shlex.split("/bin/bash -c 'make -C {} {} -j{}'".format(
                self._path['extract'],
                command,
                1 if os.cpu_count() is None else os.cpu_count())
            ),
            stdout_callback=handle_output,
            stderr_callback=handle_output,
        )

        return self
