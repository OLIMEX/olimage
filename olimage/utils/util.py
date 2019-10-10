# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Olimex Ltd.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os

import olimage.environment as env


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

        workdir = env.paths['workdir']

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