import os

from utils.printer import Printer


class Package(object):
    def __init__(self, name, workdir, config):
        """
        Hold common configurations

        :param name: package name
        :param workdir: the base workdir directory
        :param config: specific package configuration
        """
        self._name = name
        self._config = config
        self._printer = None

        # Configure paths
        self._path = {
            'package': os.path.join(workdir, 'dl', name),
            'clone': os.path.join(workdir, 'dl', name, config['refs']),
            'archive': os.path.join(workdir, 'dl', name, config['refs'] + '.tar.gz'),
            'build': os.path.join(workdir, 'build', name),
            'extract': os.path.join(workdir, 'build', name, config['refs']),
            'rootfs' : os.path.joint(workdir, 'rootfs', name)
        }

    def __str__(self):
        return self._name

    @property
    def printer(self):
        raise NotImplementedError()

    @printer.setter
    def printer(self, printer):
        raise NotImplementedError()

    @property
    def path(self):
        return self._path
