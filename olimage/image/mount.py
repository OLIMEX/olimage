import functools
import logging
import os
import re
import shutil

from olimage.core.parsers.partitions import Partition
from olimage.core.utils import Utils

logger = logging.getLogger(__name__)


class Map(object):
    def __init__(self, image, partitions):

        self._image = image
        self._partitions = partitions

        # Store partition -> mapped device dictionary
        self._devices = {}

        # Store cleanup
        self._order = []

    def __enter__(self):
        logger.info("Mapping image {}".format(self._image))

        lines = Utils.shell.run('kpartx -avs {}'.format(self._image)).decode('utf-8', 'ignore')
        for line in lines.splitlines():
            w = line.split()
            if w[0] == 'add':
                device = os.path.join('/dev/mapper', w[2])
                index = int(re.match(r'^loop\d+p(\d+)$', w[2])[1])

                # Get partition and set device
                partition: Partition
                partition = self._partitions[index - 1]
                self._devices[str(partition)] = device

                # Always add '/' at first place
                if partition.fstab.mount == '/':
                    self._order.insert(0, partition)
                else:
                    self._order.append(partition)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Unmapping image {}".format(self._image))

        Utils.shell.run('kpartx -dvs {}'.format(self._image))

    def device(self, partition):
        if isinstance(partition, Partition):
            partition = str(partition)

        for key, value in self._devices.items():
            if key == partition:
                return value

        return None


class Mount(Map):
    def __enter__(self):
        super().__enter__()

        logger.info("Mounting partitions")

        # Recreate mounting point
        if os.path.exists(self._mount):
            shutil.rmtree(self._mount)
        os.mkdir(self._mount)

        # Actual mount
        for partition in self._order:
            mount = partition.fstab.mount
            device = partition.device

            logger.debug("Mounting {} on {}".format(partition, mount))
            mount = os.path.join(self._mount, mount.lstrip('/'))

            if not os.path.exists(mount):
                Utils.shell.run('mkdir {}'.format(mount))

            Utils.shell.run('mount {} {}'.format(device, mount))

    def __exit__(self, exc_type, exc_val, exc_tb):
        # First unmount
        logger.info("Unmounting partitions")

        for part in reversed(self._order):
            mount = os.path.join(self._mount, part.fstab.mount.lstrip('/'))

            logger.debug("Unmounting {} from {}".format(part, mount))

            Utils.shell.run('umount {}'.format(mount))

        # Then unmap
        super().__exit__(exc_type, exc_val, exc_tb)


class Mounter(object):
    map = Map
    # mount = Mount
