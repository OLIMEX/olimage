import logging
import os

import olimage.environment as env

from olimage.core.utils import Utils
from olimage.core.parsers import Partitions

logger = logging.getLogger(__name__)


class FSTab(object):
    @staticmethod
    def __call__(partitions: Partitions, path: str, **kwargs) -> None:
        """
        Set hostname to etc/hosts and etc/hostname

        :param partitions: Partitions table
        :param path: Path to install files
        :return: None
        """
        for partition in partitions:
            uuid = partition.fstab.uuid
            mount = partition.fstab.mount

            logger.debug("Adding {} as UUID={} to {}".format(partition, uuid, mount))

        file = 'etc/fstab'
        source = os.path.join(env.paths['overlay'], file)
        destination = os.path.join(path, file)

        # Copy file
        Utils.shell.run("rsync -rlDHWXhv {} {}".format(source, destination))

        # Generate template
        Utils.template.install(
            destination,
            partitions=[
                {
                    'uuid': '{:36}'.format(part.fstab.uuid),
                    'mount': '{:15}'.format(part.fstab.mount),
                    'type': '{:7}'.format(part.fstab.type),
                    'options': '{:8}'.format(part.fstab.options),
                    'dump': '{:7}'.format(part.fstab.dump),
                    'pass': '{:8}'.format(part.fstab.passno)
                } for part in partitions
            ]
        )
