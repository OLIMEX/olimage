import os

import olimage.environment as env


class Util(object):
    def __init__(self, name, data):
        """
        Hold common configurations

        :param name: package name
        :param workdir: the base workdir directory
        :param data: specific package configuration
        """
        self._name = name
        self._data = data

        workdir = env.paths['workdir']

        # Configure paths
        self._paths = {
            'package': os.path.join(workdir, 'dl', name),
            'clone': os.path.join(workdir, 'dl', name, data['refs']),
            'archive': os.path.join(workdir, 'dl', name, data['refs'] + '.tar.gz'),

            'build': os.path.join(workdir, 'build', name),
            'extract': os.path.join(workdir, 'build', name, data['refs']),

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
    def data(self):
        """
        Get util configuration

        :return: dict with configuration
        """
        return self.data