import os

import olimage.environment as env

from olimage.core.utils import Utils

from .base import ServiceBase


class ServiceAptCache(ServiceBase):
    @staticmethod
    def enable(host: str, port: int) -> None:
        file = '/etc/apt/apt.conf.d/01cache'

        # Install the file
        Utils.install(file)

        # Generate template
        Utils.template.install(
            env.paths['debootstrap'] + file,
            host=host,
            port=port
        )

    @staticmethod
    def disable() -> None:
        file = env.paths['debootstrap'] + '/etc/apt/apt.conf.d/01cache'

        # Check if file exists
        if not os.path.exists(file):
            return

        # Remove configuration file
        Utils.shell.run("rm -vf {}".format(file))
