import logging
import os
import shlex
import shutil
import tarfile

from olimage.utils.stamper import PackageStamper
from olimage.utils.worker import Worker

from olimage.utils import Util

logger = logging.getLogger(__name__)


class Builder(Util):

    def __init__(self, name, config):
        super().__init__(name, config)

        # Configure stamper
        self.stamper = PackageStamper(self.paths['build'])

    def extract(self):

        path = self.paths['extract']
        if 'extracted' in self.stamper.stamps and os.path.exists(path):
            return self

        self.stamper.remove()

        # Cleanup directory
        if os.path.exists(path):
            logger.debug("Removing dirty directory: {}".format(self.paths['extract']))
            shutil.rmtree(path)

        # Extract sources
        with tarfile.open(name=self.paths['archive'], mode='r:gz') as tar:
            tar.extractall(path=self.paths['extract'])

        self.stamper.stamp('extracted')

        return self

    def make(self, command, **kwargs):
        return Worker.run(
            shlex.split("/bin/bash -c 'make -C {} {} -j{}'".format(
                self.paths['extract'],
                command,
                1 if os.cpu_count() is None else os.cpu_count())
            ),
            logger
        )
