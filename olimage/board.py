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

import yaml

import olimage.environment as environment


class Board(object):
    def __init__(self, target):
        """
        Default constructor. Scan <configs>/boards for target configuration.

        :param target: name of the board, e.g. A64-OLinuXino-1G
        """

        self._name = None
        self._config = None
        self._arch = None

        path = os.path.join(environment.paths['configs'], 'boards')
        for (_, _, files) in os.walk(path):
            for file in files:
                with open(os.path.join(path, file), 'r') as f:
                    config = yaml.full_load(f.read())
                try:
                    for key, value in config['boards'].items():
                        if target.lower() == key.lower():
                            self._config = value
                            self._name = key
                            self._arch = config['arch']
                            self._packages = config['packages']
                            break
                except KeyError:
                    continue

        if self._name is None:
            raise Exception("Target \'{}\' not found in configuration files!".format(target))

    def __str__(self):
        """
        Return board name

        :return: string with board name
        """
        return self._name

    @property
    def arch(self):
        """
        Get target architecture

        :return: target arch
        """
        return self._arch

    @property
    def packages(self):
        """
        Get BSP configuration

        :return: configuration dict
        """
        return self._packages

    @property
    def id(self):
        """
        Get target board ID

        :return: int id
        """
        return self._config['id']

    @property
    def fdt(self):
        """
        Get board default fdt

        :return: string fdt
        """
        return self._config['fdt']


