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

import functools
import logging
import os
import re
import shlex
import shutil

from olimage.utils.worker import Worker

logger = logging.getLogger(__name__)


class Mount(object):

    def __init__(self, map_only=False):
        self._obj = None
        self._image = None
        self._mount = None

        self._partitions = []

        self._map_only = map_only

    def __enter__(self):
        logger.info("Mapping image {}".format(self._image))

        output = Worker.run(shlex.split('kpartx -avs {}'.format(self._image)), logger).decode('utf-8', 'ignore')
        for line in output.splitlines():
            w = line.split()
            if w[0] == 'add':
                device = os.path.join('/dev/mapper', w[2])
                index = int(re.match(r'^loop\d+p(\d+)$', w[2])[1])
                part, cfg = list(self._obj._images['partitions'].items())[index - 1]

                # Add device to cfg
                cfg['device'] = device
                mountpoint = cfg['fstab']['mount']

                if mountpoint == '/':
                    self._partitions.insert(0, (device, part, mountpoint))
                else:
                    self._partitions.append((device, part, mountpoint))

        if self._map_only:
            return

        logger.info("Mounting partitions")
        if os.path.exists(self._mount):
            shutil.rmtree(self._mount)
        os.mkdir(self._mount)

        for device, name, mountpoint in self._partitions:
            logger.debug("Mounting {} on {}".format(name, mountpoint))
            mountpoint = os.path.join(self._mount, mountpoint.lstrip('/'))

            if not os.path.exists(mountpoint):
                os.mkdir(mountpoint)

            Worker.run(shlex.split('mount {} {}'.format(device, mountpoint)), logger)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._map_only:
            logger.info("Unmounting partitions")
            for _, name, mountpoint in reversed(self._partitions):
                logger.debug("Unmounting {} from {}".format(name, mountpoint))
                mountpoint = os.path.join(self._mount, mountpoint.lstrip('/'))

                if not os.path.exists(mountpoint):
                    os.mkdir(mountpoint)

                Worker.run(shlex.split('umount {}'.format(mountpoint)), logger)

        logger.info("Unmapping image {}".format(self._image))
        Worker.run(shlex.split('kpartx -dvs {}'.format(self._image)), logger)

    def __call__(self, f):

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            self._obj = args[0]
            self._image = self._obj._image
            self._mount = os.path.join(os.path.dirname(self._image), ".mnt")
            with self:
                return f(*args, **kwargs)
        return wrapper
