import os

import olimage.environment as env

from olimage.core.utils import Utils


class Resize(object):
    @staticmethod
    def install() -> None:
        # Install file
        Utils.install(
            [
                '/usr/lib/olinuxino/olinuxino-expand',
                '/etc/systemd/system/olinuxino-expand.service'
            ],
            mode='755')

        # Enable service
        Utils.shell.chroot("systemctl enable olinuxino-expand.service")