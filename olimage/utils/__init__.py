import os

import olimage.environment as environment


class Util(object):
    def __init__(self, name, config):
        """
        Hold common configurations

        :param name: package name
        :param workdir: the base workdir directory
        :param config: specific package configuration
        """
        self._name = name
        self._config = config

        workdir = environment.paths['workdir']

        # Configure paths
        self._paths = {
            'package': os.path.join(workdir, 'dl', name),
            'clone': os.path.join(workdir, 'dl', name, config['refs']),
            'archive': os.path.join(workdir, 'dl', name, config['refs'] + '.tar.gz'),
            'build': os.path.join(workdir, 'build', name),
            'extract': os.path.join(workdir, 'build', name, config['refs']),
            'rootfs' : os.path.join(workdir, 'rootfs', name)
        }

    def __str__(self):
        return self._name

    @property
    def paths(self):
        """
        Get util paths

        :return: dict with paths
        """
        return self._paths

    @property
    def config(self):
        """
        Get util configuration

        :return: dict with configuration
        """
        return self._confg