import olimage.environment as env

from olimage.core.utils import Utils

from .base import SetupAbstract


class SetupHostname(SetupAbstract):
    def setup(self, hostname: str) -> None:
        """
        Set hostname to etc/hosts and etc/hostname

        :param hostname: Desired hostname
        :return: None
        """
        files = [
            '/etc/hostname',
            '/etc/hosts'
        ]

        for file in files:
            Utils.install(file)
            Utils.template.install(env.paths['build'] + file, hostname=hostname)
