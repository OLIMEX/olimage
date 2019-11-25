import logging
import os

import olimage.environment as env

from olimage.core.parsers import Partitions
from olimage.core.setup import Setup
from olimage.core.utils import Utils

from olimage.core.printer import Printer

from .mount import Mounter

logger = logging.getLogger(__name__)


class Image(object):
    def __init__(self, partitions: Partitions):

        # Initialize dependency
        self._partitions = partitions

        # Global data
        self._output = env.options['output']

    @Printer("Generating blank image")
    def generate(self, size: int) -> None:
        """
        Generate black image

        :return: None
        """

        # Get size and add 500MiB size
        # size = math.ceil(self.get_size(self._rootfs)/1024/1024) + 500
        Utils.qemu.img(self._output, size)

    @Printer("Partitioning")
    def partition(self) -> None:
        """
        Partition the output blank image

        :return: None
        """

        # Create label
        logger.info("Creating disk label: msdos")
        Utils.shell.run('parted -s {} mklabel msdos'.format(self._output))

        # Create partitions
        for part in self._partitions:
            logger.info("Creating partition: {}".format(part))
            Utils.shell.run(
                'parted -s {} mkpart primary {} {} {}'.format(
                    self._output, part.parted.type,
                    part.parted.start,
                    part.parted.end
                )
            )

    @Printer("Formatting")
    @Mounter.map()
    def format(self):

        for partition in self._partitions:
            logger.info("Formatting partition: {}".format(partition))

            # Get parted related information
            device = partition.device
            fstab = partition.fstab

            opts = ''
            if type == 'ext4':
                opts = '-O ^64bit,^metadata_csum'

            # Make filesystem
            Utils.shell.run('mkfs.{} {} {}'.format(fstab.type, opts, device))
            Utils.shell.run('udevadm trigger {}'.format(device))
            Utils.shell.run('udevadm settle'.format(device))

            # Generate UUID
            fstab.uuid = Utils.shell.run(
                'blkid -s UUID -o value {}'.format(device)
            ).decode().splitlines()[0]

    @Printer("Configuring")
    def configure(self):
        Setup.fstab(self._partitions, '/olimage/output/rootfs/arm64-buster')

    @Printer("Installing")
    @Mounter.mount()
    def copy(self, source):
        exclude = ['/dev/*', '/proc/*', '/run/*', '/tmp/*', '/sys/*']
        order = []

        for part in self._partitions:

            mount = part.fstab.mount
            if mount == '/':
                order.insert(0, mount)
            else:
                order.append(mount)
                exclude.append(mount)

        mnt = os.path.join(os.path.dirname(self._output), ".mnt")
        for mount in order:
            if mount == '/':
                ex = ""
                for key in exclude:
                    ex += '--exclude="{}" '.format(key)
                Utils.shell.run('rsync -aHWXh {} {}/ {}/'.format(ex, source, mnt))
            else:
                Utils.shell.run('rsync -rLtWh {}/ {}/'.format(os.path.join(source, mount), mnt + mount))
