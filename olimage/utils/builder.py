import logging
import os
import shlex
import shutil
import tarfile

from olimage.utils.printer import Printer
from olimage.utils.stamper import PackageStamper
from olimage.utils.worker import Worker

from olimage.utils import Util

logger = logging.getLogger(__name__)


class Builder(Util):

    def __init__(self, name, config):
        super().__init__(name, config)

        # Configure stamper
        self.stamper = PackageStamper(self.paths['build'])

    @property
    def printer(self):
        return self._printer

    @printer.setter
    def printer(self, printer):
        self._printer = printer

    @Printer("Extracting archive")
    def extract(self):

        self.printer.text += " \'{}\'".format(os.path.basename(self.paths['archive']))

        if 'extracted' in self.stamper.stamps:
            return self

        # Cleanup directory
        if os.path.exists(self.paths['extract']):
            logger.debug("Removing dirty directory: {}".format(self.paths['extract']))
            shutil.rmtree(self.paths['extract'])

        # Extract sources
        with tarfile.open(name=self.paths['archive'], mode='r:gz') as tar:
            tar.extractall(path=self.paths['extract'])

        self.stamper.stamp('extracted')

        return self

    @Printer("Configuring package")
    def configure(self, command=None):

        self.printer.text += " \'{}\'".format(self)

        if 'configured' in self.stamper.stamps:
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
                self.paths['extract'],
                command,
                1 if os.cpu_count() is None else os.cpu_count())
            ),
            logger
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
                self.paths['extract'],
                command,
                1 if os.cpu_count() is None else os.cpu_count())
            ),
            logger
        )

        return self
