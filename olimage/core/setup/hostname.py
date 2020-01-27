import os

import olimage.environment as env

from olimage.core.utils import Utils


class Hostname(object):
    @staticmethod
    def __call__(hostname: str, path: str, **kwargs) -> None:
        """
        Set hostname to etc/hosts and etc/hostname

        :param hostname: Desired hostname
        :param path: Path to install files
        :return: None
        """
        files = [
            'etc/hostname',
            'etc/hosts'
        ]

        for file in files:
            source = os.path.join(env.paths['overlay'], file)
            destination = os.path.join(path, file)

            # Copy file
            Utils.shell.run("rsync -rlDHWXhv {} {}".format(source, destination))

            # Generate templates
            Utils.template.install(destination, hostname=hostname)