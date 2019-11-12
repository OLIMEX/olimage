import functools
import logging
import os
import re
import shutil

from olimage.core.utils import Utils

logger = logging.getLogger(__name__)


class Map(object):
    def __init__(self):
        self._output = None
        self._mount = None

        self._partitions = None
        self._order = []

    def __call__(self, *args, **kwargs):
        f = args[0]

        @functools.wraps(f)
        def wrapper(*args, **kwargs):

            # Get self
            from olimage.image import Image
            obj: Image = args[0]

            # Copy values
            self._output = obj._output
            self._partitions = obj._partitions
            self._mount = os.path.join(os.path.dirname(self._output), ".mnt")

            with self:
                return f(*args, **kwargs)
        return wrapper

    def __enter__(self):
        logger.info("Mapping image {}".format(self._output))

        output = Utils.shell.run('kpartx -avs {}'.format(self._output)).decode('utf-8', 'ignore')
        for line in output.splitlines():
            w = line.split()
            if w[0] == 'add':
                device = os.path.join('/dev/mapper', w[2])
                index = int(re.match(r'^loop\d+p(\d+)$', w[2])[1])

                # Get partition and set device
                partition = self._partitions[index - 1]
                partition.device = device

                # Always add '/' at first place
                if partition.fstab.mount == '/':
                    self._order.insert(0, partition)
                else:
                    self._order.append(partition)

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Unmapping image {}".format(self._output))

        Utils.shell.run('kpartx -dvs {}'.format(self._output))


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
    mount = Mount
