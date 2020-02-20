from olimage.core.utils import Utils
from olimage.core.parsers import Partitions

from .base import SetupAbstract


class SetupFstab(SetupAbstract):
    def setup(self, partitions: Partitions, path: str) -> None:
        """
        Set hostname to etc/hosts and etc/hostname

        :param partitions: Partitions table
        :param path: Path to install files
        :return: None
        """

        file = '/etc/fstab'
        Utils.install(file, path=path)

        # Generate template
        Utils.template.install(
            path + file,
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
