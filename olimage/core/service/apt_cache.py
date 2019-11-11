import os

import olimage.environment as env

from olimage.core.utils import Utils


class AptCache(object):
    @staticmethod
    def install(path: str, host: str, port: int) -> None:
        file = '/etc/apt/apt.conf.d/01cache'

        source = env.paths['overlay'] + file
        destination = path + file

        # Create destination path
        Utils.shell.chroot("mkdir -p {}".format(os.path.dirname(file)), path)

        # Copy file
        Utils.shell.run("rsync -rlDHWXhv {} {}".format(source, destination))

        # Generate template
        Utils.template.install(
            destination,
            host=host,
            port=port
        )

    @staticmethod
    def uninstall(path: str) -> None:
        file = 'etc/apt/apt.conf.d/01cache'

        # Remove configuration file
        Utils.shell.run("rm -vf {}".format(os.path.join(path, file)))