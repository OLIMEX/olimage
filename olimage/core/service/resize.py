import os

import olimage.environment as env

from olimage.core.utils import Utils


class Resize(object):
    @staticmethod
    def install() -> None:
        files = [
            '/usr/lib/olinuxino/olinuxino-expand',
            '/etc/systemd/system/olinuxino-expand.service'
        ]

        for file in files:
            source = env.paths['overlay'] + file
            destination = env.paths['destination'] + file

            # Install file
            Utils.install(source, destination, mode='755')

        # Enable service
        Utils.shell.chroot("systemctl enable olinuxino-expand.service")