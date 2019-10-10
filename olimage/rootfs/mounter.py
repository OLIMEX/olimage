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

from dependency_injector import containers, providers

from olimage.container import IocContainer
from olimage.utils import Worker

logger = logging.getLogger(__name__)


class Map(object):

    def __init__(self, partitions):
        self._image = None
        self._mount = None

        self._partitions = partitions
        self._order = []

    def __enter__(self):
        logger.info("Mapping image {}".format(self._image))

        output = Worker.run(shlex.split('kpartx -avs {}'.format(self._image)), logger).decode('utf-8', 'ignore')
        for line in output.splitlines():
            w = line.split()
            if w[0] == 'add':
                device = os.path.join('/dev/mapper', w[2])
                index = int(re.match(r'^loop\d+p(\d+)$', w[2])[1])

                # Get partition and set device
                part = self._partitions[index - 1]
                part.device = device

                # Always add '/' at first place
                if part.fstab.mount == '/':
                    self._order.insert(0, part)
                else:
                    self._order.append(part)

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Unmapping image {}".format(self._image))

        Worker.run(shlex.split('kpartx -dvs {}'.format(self._image)), logger)

    def __call__(self, f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            self._image = args[0]._image # TODO: This is GSP
            self._mount = os.path.join(os.path.dirname(self._image), ".mnt")
            with self:
                return f(*args, **kwargs)
        return wrapper


class Mount(Map):

    def __enter__(self):
        # First map
        super().__enter__()

        # Then mount
        logger.info("Mounting partitions")

        # Recreate mounting point
        if os.path.exists(self._mount):
            shutil.rmtree(self._mount)
        os.mkdir(self._mount)

        # Actual mount
        for part in self._order:
            mount = part.fstab.mount
            device = part.device

            logger.debug("Mounting {} on {}".format(part, mount))
            mount = os.path.join(self._mount, mount.lstrip('/'))

            if not os.path.exists(mount):
                os.mkdir(mount)

            Worker.run(shlex.split('mount {} {}'.format(device, mount)), logger)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # First unmount
        logger.info("Unmounting partitions")

        for part in reversed(self._order):
            mount = os.path.join(self._mount, part.fstab.mount.lstrip('/'))

            logger.debug("Unmounting {} from {}".format(part, mount))

            Worker.run(shlex.split('umount {}'.format(mount)), logger)

        # Then unmap
        super().__exit__(exc_type, exc_val, exc_tb)


class Mounter(containers.DeclarativeContainer):
    mount = providers.Factory(Mount, partitions=IocContainer.partitions)
    map = providers.Factory(Map, partitions=IocContainer.partitions)
