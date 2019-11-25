import os

import olimage.environment as env

from olimage.core.utils import Utils


class AptCache(object):
    @staticmethod
    def install(host: str, port: int) -> None:
        file = '/etc/apt/apt.conf.d/01cache'

        source = env.paths['overlay'] + file
        destination = env.paths['debootstrap'] + file

        # Install file
        Utils.install(source, destination)

        # Generate template
        Utils.template.install(
            destination,
            host=host,
            port=port
        )

    @staticmethod
    def uninstall() -> None:
        file = '/etc/apt/apt.conf.d/01cache'
        path = env.paths['debootstrap'] + file

        # Check if file exists
        if not os.path.exists(path):
            return

        # Remove configuration file
        Utils.shell.run("rm -vf {}".format(path))