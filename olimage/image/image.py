import logging
import os

import olimage.environment as env

from olimage.core.io import Output
from olimage.core.parsers import Partitions
from olimage.core.setup import Setup
from olimage.core.utils import Utils

from .mount import Mounter

logger = logging.getLogger(__name__)


class Image(object):
    def __init__(self, partitions: Partitions):

        # Initialize dependency
        self._partitions = partitions

        # Global data
        self._output = env.options['output']

    def generate(self) -> None:
        """
        Generate black image

        :return: None
        """

        size = 0
        for _dir, _, file in os.walk(env.paths['debootstrap']):
            for f in file:
                fp = os.path.join(_dir, f)

                if not os.path.islink(fp):
                    size += os.path.getsize(fp)

        # Get size and add 500MiB size
        size = max((size >> 20) + 500, env.options['size'])

        with Output.step("Generating black image with size: {}MiB".format(size)):
            Utils.qemu.img(self._output, size)

    def partition(self) -> None:
        """
        Partition the output blank image

        :return: None
        """

        # Create label
        with Output.step("Creating msdos partition table"):
            Utils.shell.run('parted -s {} mklabel msdos'.format(self._output))

        # Create partitions
        for partition in self._partitions:
            with Output.substep("Creating partition: \'{}\'".format(str(partition))):
                Utils.shell.run(
                    'parted -s {} mkpart primary {} {} {}'.format(
                        self._output, partition.parted.type,
                        partition.parted.start,
                        partition.parted.end
                    )
            )

    # @Mounter.map()
    def format(self):

        with Mounter.map(self._output, self._partitions) as m:
            for partition in self._partitions:
                with Output.substep("Formating partition: \'{}\'".format(str(partition))):
                    # Get parted related information
                    device = m.device(partition)

                    opts = ''
                    if partition.fstab.type == 'ext4':
                        opts = '-O ^64bit,^metadata_csum'

                    # Make filesystem
                    Utils.shell.run('mkfs.{} {} {}'.format(partition.fstab.type, opts, device))
                    Utils.shell.run('udevadm trigger {}'.format(device))
                    Utils.shell.run('udevadm settle'.format(device))

    def configure(self):
        # # Generate UUID
        # partition.fstab.uuid = Utils.shell.run(
        #     'blkid -s UUID -o value {}'.format(device)
        # ).decode().splitlines()[0]

        with Output.step("Generating /etc/fstab"):
            Setup.fstab(self._partitions, env.paths)

    # @Mounter.mount()
    def copy(self, source):
        exclude = ['/dev/*', '/proc/*', '/run/*', '/tmp/*', '/sys/*']
        order = []

        with Mounter.mount(self._output, self._partitions) as m:
            for part in self._partitions:

                mount = part.fstab.mount
                if mount == '/':
                    order.insert(0, mount)
                else:
                    order.append(mount)
                    exclude.append(mount)

        # mnt = os.path.join(os.path.dirname(self._output), ".mnt")
        # for mount in order:
        #     if mount == '/':
        #         ex = ""
        #         for key in exclude:
        #             ex += '--exclude="{}" '.format(key)
        #         Utils.shell.run('rsync -aHWXh {} {}/ {}/'.format(ex, source, mnt))
        #     else:
        #         Utils.shell.run('rsync -rLtWh {}/ {}/'.format(os.path.join(source, mount), mnt + mount))
