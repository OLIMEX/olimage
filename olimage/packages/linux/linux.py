import logging
import shlex
import os

from olimage.packages import Package
from olimage.utils.downloader import Downloader
from olimage.utils.builder import Builder
from olimage.utils.worker import Worker

logger = logging.getLogger(__name__)


class Linux(Package):

    def __init__(self, config):

        self._name = 'linux'
        self._config = config

        self._builder = Builder(self._name, self._config)

        # Initialize callback methods
        callbacks = {
            'download':     self._download,
            'configure':    self._configure,
            'build':        self._build,
            'package':      self._package,
            'install':      self._install,
        }
        super().__init__(**callbacks)

    @staticmethod
    def alias():
        return 'linux'

    @property
    def dependency(self):
        try:
            return self._config['depends']
        except KeyError:
            return []

    def __str__(self):
        return self._name

    def _download(self):
        """
        Download sources. Currently only git is supported

        :return: self
        """
        Downloader(self._name, self._config).download()
        self._builder.extract()
        return self

    def _configure(self):
        """
        Configure sources using defconfig

        :return: self
        """

        arch = self._config['arch']
        defconfig = 'defconfig'

        if self._config['defconfig'] is not None:
            defconfig = self._config['defconfig'] + '_defconfig'

        # Make defconfig
        self._builder.make("ARCH={} {}".format(arch, defconfig))

        # Apply fragments
        path = self._builder.paths['extract']
        script = os.path.join(path, 'scripts/kconfig/merge_config.sh')
        config = os.path.join(path, '.config')
        fragment = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fragments/test.fragment')

        # First merge config files
        Worker.run(shlex.split("/bin/bash -c '{} -m {} {}'".format(script, config, fragment)))

        # Second, regenerate config file
        self._builder.make("ARCH={} oldconfig".format(arch))

    def _build(self):
        return
        self._builder.make("ARCH={} CROSS_COMPILE={} {}".format(
                self._config['arch'],
                self._config['toolchain']['prefix'],
                ' '.join(self._config['targets'])))

    def _package(self):
        arch = self._config['arch']
        toolchain = self._config['toolchain']['prefix']

        self._builder.make("LOCALVERSION=-1-olimex ARCH={} CROSS_COMPILE={} deb-pkg".format(arch, toolchain))

    def _install(self):
        pass



