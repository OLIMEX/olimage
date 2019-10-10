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

import olimage.environment as env
import olimage.rootfs


class Partitions(object):
    def __init__(self):
        """
        Initialize partitions

        Note: Config file read must be delayed
        """
        self._partitions = []
        self._loaded = False

    def __iter__(self):
        self._load()
        self._iter = iter(self._partitions)
        return self

    def __next__(self):
        return next(self._iter)

    def __getitem__(self, item):
        self._load()
        return self._partitions[item]

    def _load(self):
        """
        Load configuration

        :return: None
        """
        if self._loaded:
            return

        # Read configuration file
        with open(os.path.join(env.paths['configs'], 'partitions.yaml')) as f:
            data = yaml.full_load(f.read())['partitions']

        # Generate mapping
        for key, value in data.items():
            self._partitions.append(olimage.rootfs.ORM(key, value))

        self._loaded = True
